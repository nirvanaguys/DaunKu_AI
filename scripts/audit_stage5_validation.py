#!/usr/bin/env python3
"""
audit_stage5_validation.py — DaunKu AI Stage 5 Final Validation Script
Menjalankan pemeriksaan komprehensif terhadap:
- artifacts/canonical_manifest.csv
- configs/label_mapping.yaml
- reports/canonical_dataset_design.md
- reports/duplicate_groups.csv
- reports/potential_data_leakage.csv
"""

import csv
import yaml
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "canonical_manifest.csv"
YAML_PATH = PROJECT_ROOT / "configs" / "label_mapping.yaml"
DUP_GROUPS_PATH = PROJECT_ROOT / "reports" / "duplicate_groups.csv"
LEAK_PAIRS_PATH = PROJECT_ROOT / "reports" / "potential_data_leakage.csv"
STAGE3_JSON_PATH = PROJECT_ROOT / "artifacts" / "duplicate_audit.json"

def run_audit():
    print("=" * 80)
    print("STARTING AUDIT: DAUNKU AI STAGE 5 CANONICAL DATASET VALIDATION")
    print("=" * 80)
    
    issues = []
    
    # -------------------------------------------------------------
    # AUDIT A: MANIFEST DAN STATUS
    # -------------------------------------------------------------
    print("\n[AUDIT A] Memeriksa Manifest dan Konsistensi Status...")
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        manifest_rows = list(reader)
        manifest_header = reader.fieldnames

    total_rows = len(manifest_rows)
    print(f"  1. Total baris manifest: {total_rows:,} (Harus tepat 85.022)")
    if total_rows != 85022:
        issues.append(("AUDIT_A_ROW_COUNT", "CRITICAL", f"Jumlah baris manifest {total_rows} != 85.022"))

    unique_paths = set(r["relative_path"] for r in manifest_rows)
    print(f"  2. Total path relatif unik: {len(unique_paths):,} (Harus 85.022)")
    if len(unique_paths) != 85022:
        issues.append(("AUDIT_A_UNIQUE_PATHS", "CRITICAL", f"Path unik {len(unique_paths)} != 85.022"))

    # Status counts in manifest
    mapping_status_counts = Counter(r["mapping_status"] for r in manifest_rows)
    usage_status_counts = Counter(r["usage_status"] for r in manifest_rows)
    condition_counts = Counter(r["plant_condition"] for r in manifest_rows)

    print(f"  3. Rincian mapping_status aktual manifest:\n     {dict(mapping_status_counts)}")
    print(f"  4. Rincian usage_status aktual manifest:\n     {dict(usage_status_counts)}")
    print(f"  5. Rincian plant_condition aktual manifest:\n     {dict(condition_counts)}")

    # Check for Unknown treated as Healthy
    unknown_as_healthy = []
    for r in manifest_rows:
        if r["plant_condition"] == "Unknown":
            if "healthy" in r["canonical_label"].lower():
                unknown_as_healthy.append(r)
            if r["eligible_condition"] == "True":
                unknown_as_healthy.append(r)
    print(f"  6. Unknown dianggap Healthy atau eligible condition: {len(unknown_as_healthy)} (Harus 0)")
    if unknown_as_healthy:
        issues.append(("AUDIT_A_UNKNOWN_AS_HEALTHY", "CRITICAL", f"Ditemukan {len(unknown_as_healthy)} baris Unknown yang dianggap Healthy / eligible condition"))

    # Load configs/label_mapping.yaml
    with open(YAML_PATH, "r", encoding="utf-8") as yf:
        yaml_data = yaml.safe_load(yf)
    yaml_mappings = yaml_data.get("label_mappings", [])
    print(f"  7. Total entri label di configs/label_mapping.yaml: {len(yaml_mappings)}")
    
    yaml_mapping_status_counts = Counter(x["mapping_status"] for x in yaml_mappings)
    yaml_usage_status_counts = Counter(x["usage_status"] for x in yaml_mappings)
    print(f"     Status mapping di YAML: {dict(yaml_mapping_status_counts)}")
    print(f"     Status usage di YAML: {dict(yaml_usage_status_counts)}")

    # -------------------------------------------------------------
    # AUDIT B: DSU DAN PARENT GROUP
    # -------------------------------------------------------------
    print("\n[AUDIT B] Memeriksa DSU dan Integritas Parent Group...")
    parent_to_files = defaultdict(list)
    file_to_parent = {}
    for r in manifest_rows:
        p_grp = r["parent_source_group_id"]
        norm_p = r["relative_path"].replace("/", "\\")
        parent_to_files[p_grp].append(r)
        file_to_parent[norm_p] = p_grp

    total_parents = len(parent_to_files)
    print(f"  1. Total parent_source_group_id: {total_parents:,}")

    # Sizes distribution
    sizes = [len(v) for v in parent_to_files.values()]
    print(f"     Ukuran parent group: min={min(sizes)}, max={max(sizes)}, mean={sum(sizes)/len(sizes):.2f}, median={sorted(sizes)[len(sizes)//2]}")
    singletons = sum(1 for s in sizes if s == 1)
    multi_file_parents = sum(1 for s in sizes if s > 1)
    print(f"     Parent kelompok tunggal (1 gambar): {singletons:,}")
    print(f"     Parent kelompok jamak (>1 gambar): {multi_file_parents:,}")

    # Check Exact Duplicate Groups from reports/duplicate_groups.csv
    dup_group_to_parents = defaultdict(set)
    dup_group_count = 0
    with open(DUP_GROUPS_PATH, "r", encoding="utf-8") as df:
        for row in csv.DictReader(df):
            gid = row["Duplicate Group ID"]
            fp = row["File Path"].replace("/", "\\")
            if fp in file_to_parent:
                dup_group_to_parents[gid].add(file_to_parent[fp])
    
    dup_split_across_parents = {k: v for k, v in dup_group_to_parents.items() if len(v) > 1}
    print(f"  2. Total exact duplicate groups diperiksa: {len(dup_group_to_parents):,}")
    print(f"     Exact duplicate groups terpecah lintas parent: {len(dup_split_across_parents)} (Harus 0)")
    if dup_split_across_parents:
        issues.append(("AUDIT_B_DUP_SPLIT", "CRITICAL", f"Terdapat {len(dup_split_across_parents)} exact duplicate group yang terpecah ke parent berbeda!"))

    # Check Leaf Image Dataset parent mapping
    leaf_orig_stems = {}
    leaf_aug_files = []
    for r in manifest_rows:
        rel = r["relative_path"]
        if "Leaf Image Dataset" in rel:
            if "resize plant_leaves dataset(1545)" in rel:
                stem = Path(rel).stem
                leaf_orig_stems[stem] = r["parent_source_group_id"]
            elif "augmentation dataset(12360)" in rel:
                leaf_aug_files.append(r)

    print(f"  3. Leaf Image Dataset:")
    print(f"     Foto asli (resize): {len(leaf_orig_stems):,}")
    print(f"     Foto augmentasi: {len(leaf_aug_files):,}")

    aug_mapped = 0
    aug_orphans = []
    for aug in leaf_aug_files:
        stem = Path(aug["relative_path"]).stem
        clean_stem = re.sub(r"_\d+_\d+$", "", stem)
        if clean_stem in leaf_orig_stems:
            expected_parent = leaf_orig_stems[clean_stem]
            actual_parent = aug["parent_source_group_id"]
            if expected_parent == actual_parent:
                aug_mapped += 1
            else:
                aug_orphans.append((aug["relative_path"], "PARENT_MISMATCH", clean_stem))
        else:
            aug_orphans.append((aug["relative_path"], "ORPHAN_NO_ORIGINAL", clean_stem))

    print(f"     Augmentasi berhasil dipetakan ke parent foto asli: {aug_mapped:,} / {len(leaf_aug_files):,} ({aug_mapped/len(leaf_aug_files)*100:.2f}%)")
    print(f"     Augmentasi tanpa parent/mismatch: {len(aug_orphans)} (Harus 0)")
    if aug_orphans:
        issues.append(("AUDIT_B_LEAF_ORPHANS", "CRITICAL", f"Ditemukan {len(aug_orphans)} augmentasi Leaf Image tanpa parent atau mismatch"))

    # Check Natural Background Holdout separation
    holdout_parents = set(r["parent_source_group_id"] for r in manifest_rows if r["usage_status"] == "natural_background_holdout")
    included_parents = set(r["parent_source_group_id"] for r in manifest_rows if r["usage_status"] == "included")
    overlap_holdout_included = holdout_parents.intersection(included_parents)
    print(f"  4. Natural Background Holdout Parents: {len(holdout_parents):,}")
    print(f"     Overlap antara Holdout Parent dan Included Parent: {len(overlap_holdout_included)} (Harus 0)")
    if overlap_holdout_included:
        issues.append(("AUDIT_B_HOLDOUT_LEAKAGE", "HIGH", f"Holdout parent berbagi {len(overlap_holdout_included)} grup dengan included data"))

    # Check 10 Rose Conflicting Images
    conflict_rows = [r for r in manifest_rows if r["mapping_status"] == "label_conflict"]
    conflict_parents = set(r["parent_source_group_id"] for r in conflict_rows)
    print(f"  5. Baris berstatus label_conflict (Mawar): {len(conflict_rows)} (Harus tepat 50)")
    print(f"     Parent groups untuk 50 file mawar konflik: {len(conflict_parents)}")
    for cr in conflict_rows:
        if cr["usage_status"] != "quarantined":
            issues.append(("AUDIT_B_CONFLICT_NOT_QUARANTINED", "CRITICAL", f"File konflik {cr['relative_path']} tidak berstatus quarantined"))

    # -------------------------------------------------------------
    # AUDIT C: REKONSILIASI 1.280 PASANGAN POTENTIAL LEAKAGE
    # -------------------------------------------------------------
    print("\n[AUDIT C] Memeriksa Rekonsiliasi 1.280 Pasangan Potential Data Leakage...")
    leak_pairs = []
    risk_counter = Counter()
    dist_counter = Counter()
    leak_same_parent = 0
    leak_diff_parent = 0

    if LEAK_PAIRS_PATH.exists():
        with open(LEAK_PAIRS_PATH, "r", encoding="utf-8") as lf:
            for row in csv.DictReader(lf):
                leak_pairs.append(row)
                risk_counter[row.get("Risk Level")] += 1
                cat = row.get("Leakage Category", "")
                m = re.search(r"dist=(\d+)", cat)
                if m:
                    d = int(m.group(1))
                    dist_counter[d] += 1
                
                f1 = row.get("File 1", "").replace("\\", "/")
                f2 = row.get("File 2", "").replace("\\", "/")
                p1 = file_to_parent.get(f1.replace("/", "\\"))
                p2 = file_to_parent.get(f2.replace("/", "\\"))
                if p1 and p2:
                    if p1 == p2:
                        leak_same_parent += 1
                    else:
                        leak_diff_parent += 1

    print(f"  1. Total pasangan potential leakage pada CSV Tahap 3.1: {len(leak_pairs):,}")
    print(f"     Distribusi Risiko: {dict(risk_counter)}")
    d_le_1 = sum(dist_counter[d] for d in range(2))
    d_2_to_10 = sum(dist_counter[d] for d in range(2, 11))
    print(f"     Pasangan dengan dHash <= 1 (Identik/Hampir Identik): {d_le_1:,}")
    print(f"     Pasangan dengan dHash 2..10 (Variasi Near-Duplicate): {d_2_to_10:,}")
    print(f"  2. Evaluasi terhadap DSU Stage 5:")
    print(f"     Pasangan yang saat ini berbagi parent_source_group_id: {leak_same_parent:,}")
    print(f"     Pasangan yang BELUM berbagi parent_source_group_id (unverified candidate near-duplicates): {leak_diff_parent:,}")

    # -------------------------------------------------------------
    # AUDIT D: TASK ELIGIBILITY
    # -------------------------------------------------------------
    print("\n[AUDIT D] Memeriksa Task Eligibility & Kepatuhan Aturan...")
    task_keys = ["species_id", "condition", "disease_diagnosis", "leaf_detection"]
    task_stats = {}

    for tk in task_keys:
        col = f"eligible_{tk}"
        eligible = [r for r in manifest_rows if r[col] == "True"]
        ineligible = [r for r in manifest_rows if r[col] == "False"]
        
        # Breakdown of ineligible
        unknown_lbl = sum(1 for r in ineligible if r["plant_condition"] == "Unknown")
        quarantined = sum(1 for r in ineligible if r["usage_status"] == "quarantined")
        holdout = sum(1 for r in ineligible if r["usage_status"] == "natural_background_holdout")
        excluded = sum(1 for r in ineligible if r["usage_status"] == "excluded_from_task")
        pending = sum(1 for r in ineligible if r["usage_status"] == "pending_review")

        task_stats[tk] = {
            "eligible": len(eligible),
            "ineligible": len(ineligible),
            "unknown_cond": unknown_lbl,
            "quarantined": quarantined,
            "holdout": holdout,
            "excluded_from_task": excluded,
            "pending_review": pending
        }

    for tk, st in task_stats.items():
        print(f"  - Task {tk}: Eligible={st['eligible']:,}, Ineligible={st['ineligible']:,} (Quarantined={st['quarantined']:,}, Excluded={st['excluded_from_task']:,}, Pending={st['pending_review']:,})")

    # Specific assertions
    # 1. Coffee check
    coffee_disease_eligible = [r for r in manifest_rows if "Klasifikasi Penyakit Daun Kopi" in r["source_dataset"] and r["eligible_disease_diagnosis"] == "True"]
    coffee_det_eligible = [r for r in manifest_rows if "Klasifikasi Penyakit Daun Kopi" in r["source_dataset"] and r["eligible_leaf_detection"] == "True"]
    print(f"  1. Daun Kopi eligible disease diagnosis: {len(coffee_disease_eligible)} (Harus 0)")
    print(f"     Daun Kopi eligible leaf detection: {len(coffee_det_eligible)} (Harus 3.139)")
    if coffee_disease_eligible:
        issues.append(("AUDIT_D_COFFEE_DISEASE", "CRITICAL", f"Daun Kopi masuk disease classification ({len(coffee_disease_eligible)} file)!"))

    # 2. Yellow Disease check
    yd_disease_eligible = [r for r in manifest_rows if "Yellow Disease" in r["source_dataset"] and r["eligible_disease_diagnosis"] == "True"]
    yd_provisional = [r for r in manifest_rows if "Yellow Disease" in r["source_dataset"] and r["mapping_status"] == "provisional"]
    print(f"  2. Yellow Disease eligible disease diagnosis: {len(yd_disease_eligible)} (Harus 0)")
    print(f"     Yellow Disease status provisional: {len(yd_provisional)} / 5.095")
    if yd_disease_eligible:
        issues.append(("AUDIT_D_YELLOW_DISEASE", "CRITICAL", f"Yellow Disease masuk disease diagnosis ({len(yd_disease_eligible)} file)!"))

    # 3. Jasmine Initial stage check
    jasmine_init_disease = [r for r in manifest_rows if "AJLCD-2025" in r["source_dataset"] and r["original_label"] == "Initial stage" and r["eligible_disease_diagnosis"] == "True"]
    print(f"  3. Jasmine Initial stage eligible disease diagnosis: {len(jasmine_init_disease)} (Harus 0)")
    if jasmine_init_disease:
        issues.append(("AUDIT_D_JASMINE_INITIAL", "CRITICAL", f"Jasmine Initial stage masuk disease diagnosis ({len(jasmine_init_disease)} file)!"))

    # 4. Background images check
    bg_disease = [r for r in manifest_rows if "background" in r["original_label"].lower() and r["eligible_disease_diagnosis"] == "True"]
    print(f"  4. Background images eligible disease diagnosis: {len(bg_disease)} (Harus 0)")
    if bg_disease:
        issues.append(("AUDIT_D_BG_DISEASE", "CRITICAL", f"Background image masuk disease diagnosis ({len(bg_disease)} file)!"))

    # -------------------------------------------------------------
    # AUDIT E: NATURAL BACKGROUND DAN QUARANTINE
    # -------------------------------------------------------------
    print("\n[AUDIT E] Memeriksa Rekonsiliasi Natural Background & Karantina...")
    # Marigold natural background
    marigold_holdout_manifest = [r for r in manifest_rows if r["usage_status"] == "natural_background_holdout"]
    by_ds_holdout = Counter(r["source_dataset"] for r in marigold_holdout_manifest)
    print(f"  1. Total baris natural_background_holdout pada manifest: {len(marigold_holdout_manifest):,}")
    for ds, cnt in by_ds_holdout.items():
        print(f"     - {ds}: {cnt:,} file instances")

    # Rose conflicting instances
    rose_conflict_manifest = [r for r in manifest_rows if r["mapping_status"] == "label_conflict"]
    by_ds_conflict = Counter(r["source_dataset"] for r in rose_conflict_manifest)
    print(f"  2. Total file instance mawar konflik pada manifest: {len(rose_conflict_manifest):,}")
    for ds, cnt in by_ds_conflict.items():
        print(f"     - {ds}: {cnt:,} file instances")

    # Initial stage Jasmine
    jasmine_init_manifest = [r for r in manifest_rows if r["source_dataset"].startswith("Arabian Jasmine") and r["original_label"] == "Initial stage"]
    print(f"  3. Initial stage Jasmine pada manifest: {len(jasmine_init_manifest):,} (Harus 726)")

    # Ambiguous specimen folders (Rosa/Rosa, Tagetes/Tagetes, Hibiscus/Hibiscus, strip)
    ambiguous_manifest = [r for r in manifest_rows if r["mapping_status"] == "ambiguous" and r["original_label"] != "Initial stage"]
    by_orig_ambiguous = Counter(f"{r['source_dataset']} :: {r['original_label']}" for r in ambiguous_manifest)
    print(f"  4. Spesimen ambigu (di luar Initial stage): {len(ambiguous_manifest):,} (Harus 490)")
    for k, v in by_orig_ambiguous.items():
        print(f"     - {k}: {v:,} file")

    # Check 230 Rosa/Rosa condition
    rosa_rosa = [r for r in manifest_rows if r["original_label"] == "Rosa / Rosa"]
    rosa_rosa_healthy = [r for r in rosa_rosa if r["plant_condition"] == "Healthy"]
    print(f"  5. Foto Rosa/Rosa: {len(rosa_rosa):,}, dipetakan ke Healthy: {len(rosa_rosa_healthy)} (Harus 0)")
    if rosa_rosa_healthy:
        issues.append(("AUDIT_E_ROSA_ROSA_HEALTHY", "CRITICAL", f"Rosa/Rosa sebanyak {len(rosa_rosa_healthy)} dipetakan ke Healthy tanpa bukti!"))

    print("\n" + "=" * 80)
    print(f"AUDIT SUMMARY: Ditemukan {len(issues)} isu kritis/inkonsistensi.")
    print("=" * 80)
    return {
        "manifest_rows": manifest_rows,
        "mapping_status_counts": mapping_status_counts,
        "usage_status_counts": usage_status_counts,
        "condition_counts": condition_counts,
        "yaml_mapping_status_counts": yaml_mapping_status_counts,
        "yaml_usage_status_counts": yaml_usage_status_counts,
        "total_parents": total_parents,
        "sizes": sizes,
        "singletons": singletons,
        "multi_file_parents": multi_file_parents,
        "dup_group_count": len(dup_group_to_parents),
        "dup_split_across_parents": len(dup_split_across_parents),
        "aug_mapped": aug_mapped,
        "aug_orphans": aug_orphans,
        "holdout_parents_count": len(holdout_parents),
        "overlap_holdout_included": len(overlap_holdout_included),
        "leak_pairs_count": len(leak_pairs),
        "leak_risk_counter": dict(risk_counter),
        "leak_dist_counter": dict(dist_counter),
        "leak_same_parent": leak_same_parent,
        "leak_diff_parent": leak_diff_parent,
        "task_stats": task_stats,
        "marigold_holdout_manifest": len(marigold_holdout_manifest),
        "by_ds_holdout": dict(by_ds_holdout),
        "rose_conflict_manifest": len(rose_conflict_manifest),
        "by_ds_conflict": dict(by_ds_conflict),
        "jasmine_init_manifest": len(jasmine_init_manifest),
        "ambiguous_manifest": len(ambiguous_manifest),
        "by_orig_ambiguous": dict(by_orig_ambiguous),
        "rosa_rosa_count": len(rosa_rosa),
        "rosa_rosa_healthy": len(rosa_rosa_healthy),
        "issues": issues
    }

if __name__ == "__main__":
    run_audit()
