#!/usr/bin/env python3
"""
phase1_audit_splits.py — DaunKu AI Stage 6 Phase 1: Audit Built-in Splits
"""

import csv
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "canonical_manifest.csv"
DUP_GROUPS_PATH = PROJECT_ROOT / "reports" / "duplicate_groups.csv"

def audit_builtin_splits():
    print("=" * 80)
    print("PHASE 1: AUDIT BUILT-IN SPLITS ACROSS 14 DATASETS")
    print("=" * 80)

    ds_split_stats = defaultdict(lambda: defaultdict(int))
    ds_classes_per_split = defaultdict(lambda: defaultdict(set))
    ds_parents_per_split = defaultdict(lambda: defaultdict(set))
    ds_total_files = Counter()

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ds = r["source_dataset"]
            sp = r["source_split"]
            lbl = r["original_label"]
            p_grp = r["parent_source_group_id"]
            
            ds_split_stats[ds][sp] += 1
            ds_classes_per_split[ds][sp].add(lbl)
            ds_parents_per_split[ds][sp].add(p_grp)
            ds_total_files[ds] += 1

    # Check cross-split parent groups per dataset
    ds_split_leakage_parents = {}
    for ds in ds_split_stats:
        split_names = [s for s in ds_split_stats[ds] if s != "unsplit"]
        if len(split_names) > 1:
            all_parent_occurrences = defaultdict(set)
            for sp in split_names:
                for p in ds_parents_per_split[ds][sp]:
                    all_parent_occurrences[p].add(sp)
            cross_parents = {p: splits for p, splits in all_parent_occurrences.items() if len(splits) > 1}
            ds_split_leakage_parents[ds] = len(cross_parents)
        else:
            ds_split_leakage_parents[ds] = 0

    print(f"\nAudit Summary per Dataset:")
    print("-" * 80)
    for ds in sorted(ds_split_stats.keys()):
        stats = ds_split_stats[ds]
        total = ds_total_files[ds]
        splits_str = ", ".join(f"{k}: {v:,}" for k, v in stats.items())
        cross_cnt = ds_split_leakage_parents[ds]
        print(f"Dataset: {ds}")
        print(f"  Total Files: {total:,}")
        print(f"  Splits: {splits_str}")
        print(f"  Parent groups cross-split: {cross_cnt:,}")
        for sp in sorted(stats.keys()):
            n_cls = len(ds_classes_per_split[ds][sp])
            n_par = len(ds_parents_per_split[ds][sp])
            print(f"    - [{sp}]: {stats[sp]:,} files, {n_cls} classes, {n_par:,} parent groups")
        print()

    return {
        "ds_split_stats": ds_split_stats,
        "ds_classes_per_split": ds_classes_per_split,
        "ds_parents_per_split": ds_parents_per_split,
        "ds_split_leakage_parents": ds_split_leakage_parents,
        "ds_total_files": ds_total_files
    }

if __name__ == "__main__":
    audit_builtin_splits()
