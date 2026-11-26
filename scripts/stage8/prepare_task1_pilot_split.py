#!/usr/bin/env python3
"""
prepare_task1_pilot_split.py — Stage 8.1 Task 1 Pilot Split & Data Validation
Proyek: DaunKu AI

Fungsi:
1. Memverifikasi subset baseline 68 single-species pada artifacts/splits/split_manifest.csv
   (READ-ONLY terhadap Dataset/, canonical_manifest.csv, label_mapping.yaml, dan split Stage 6).
2. Memverifikasi konsistensi label mapping, ketiadaan 37 label kombinasi multi-spesies,
   ketiadaan Unknown/quarantined, serta keterbacaan path file pada 37.408 gambar Train Stage 6.
3. Membagi HANYA Train Stage 6 (37.408 gambar) menjadi ~85% inner_train dan ~15% inner_val
   berdasarkan meta_component_id dengan seed=42 dan stratifikasi kelas tanpa memecah grup.
4. Menyimpan manifest inner_train, inner_val, class_mapping.json, dan ringkasan split.

PENTING:
- Stage 6 Validation (6.068 gambar) TIDAK digunakan untuk pilot ini.
- Locked Test (6.047 gambar) TIDAK pernah dibaca untuk training atau validasi.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Task 1 68 single-species pilot inner_train/inner_val split.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--dataset-root", type=Path, default=None, help="Path to Dataset/ directory (default: project_root/Dataset)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--inner-val-ratio", type=float, default=0.15)
    parser.add_argument("--verify-pil-sample", type=int, default=200, help="Number of random images to open with PIL for readability check (0 to skip, -1 for all).")
    return parser.parse_args()


def greedy_stratified_group_split(
    train_df: pd.DataFrame,
    group_col: str = "meta_component_id",
    label_col: str = "plant_species",
    val_ratio: float = 0.15,
    seed: int = 42,
) -> tuple[set[str], set[str]]:
    """
    Deterministic group-aware stratified split (~85% inner_train / ~15% inner_val).
    Guarantees:
    - Every meta_component_id stays intact in exactly one split (0 group leakage).
    - Every class present in >=2 meta_components appears in both inner_train and inner_val.
    """
    rng = random.Random(seed)

    # Group -> class counts
    group_labels: dict[str, Counter] = defaultdict(Counter)
    for g, lbl in zip(train_df[group_col].astype(str), train_df[label_col].astype(str)):
        group_labels[g][lbl] += 1

    # Total counts per class
    total_class_counts = Counter(train_df[label_col].astype(str))
    target_val_counts = {c: max(1.0, cnt * val_ratio) for c, cnt in total_class_counts.items()}

    # Sort classes from rarest to most common (by number of distinct groups)
    class_to_groups: dict[str, list[str]] = defaultdict(list)
    for g, cnts in group_labels.items():
        # Primary label for group ordering
        primary_lbl = cnts.most_common(1)[0][0]
        class_to_groups[primary_lbl].append(g)

    # Shuffle groups deterministically within each class
    for lbl in sorted(class_to_groups.keys()):
        class_to_groups[lbl].sort()
        rng.shuffle(class_to_groups[lbl])

    val_groups: set[str] = set()
    train_groups: set[str] = set()
    current_val_counts: Counter = Counter()

    # Order classes by fewest groups first so rare classes always get >=1 group in both splits
    ordered_classes = sorted(class_to_groups.keys(), key=lambda c: (len(class_to_groups[c]), c))

    for lbl in ordered_classes:
        groups = class_to_groups[lbl]
        if len(groups) < 2:
            raise ValueError(f"Kelas '{lbl}' hanya memiliki {len(groups)} meta_component_id di Train; tidak dapat dibagi ke inner_train & inner_val tanpa memecah grup.")

        # Always guarantee at least 1 group in inner_train and 1 group in inner_val
        assigned_val_for_lbl = 0
        assigned_train_for_lbl = 0

        for idx, g in enumerate(groups):
            if g in val_groups or g in train_groups:
                continue
            remaining = len(groups) - idx
            g_size = sum(group_labels[g].values())

            if assigned_train_for_lbl == 0 and remaining == 1:
                # Must keep at least 1 group in train
                train_groups.add(g)
                assigned_train_for_lbl += 1
            elif assigned_val_for_lbl == 0 and remaining >= 2:
                # Guarantee at least 1 group in val for this class
                val_groups.add(g)
                current_val_counts.update(group_labels[g])
                assigned_val_for_lbl += 1
            elif (current_val_counts[lbl] + g_size <= target_val_counts[lbl] * 1.00) and (assigned_train_for_lbl > 0 or remaining > 1):
                val_groups.add(g)
                current_val_counts.update(group_labels[g])
                assigned_val_for_lbl += 1
            else:
                train_groups.add(g)
                assigned_train_for_lbl += 1

    return train_groups, val_groups


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    dataset_root = args.dataset_root.resolve() if args.dataset_root else (project_root / "Dataset")

    split_manifest_path = project_root / "artifacts" / "splits" / "split_manifest.csv"
    label_mapping_path = project_root / "configs" / "label_mapping.yaml"
    out_dir = project_root / "artifacts" / "splits" / "task1_pilot"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/6] Membaca manifest: {split_manifest_path}")
    sm = pd.read_csv(split_manifest_path, low_memory=False)
    with open(label_mapping_path, "r", encoding="utf-8") as f:
        lm = yaml.safe_load(f)

    # Filter active Task 1 (species_id)
    active_sp = sm[sm["split_species_id"].isin(["train", "validation", "test"])].copy()
    is_combo = active_sp["plant_species"].astype(str).str.contains(" / ", regex=False)
    single_df = active_sp[~is_combo].copy()
    combo_df = active_sp[is_combo].copy()

    # Verify exact Stage 7 reference counts
    n_total_single = len(single_df)
    n_train = int((single_df["split_species_id"] == "train").sum())
    n_val = int((single_df["split_species_id"] == "validation").sum())
    n_test = int((single_df["split_species_id"] == "test").sum())
    n_combo = len(combo_df)
    n_classes = int(single_df["plant_species"].nunique())

    print(f"[2/6] Verifikasi angka acuan Stage 7:")
    print(f"      68 single-species total : {n_total_single} (Train={n_train}, Val={n_val}, Test={n_test})")
    print(f"      37 combo excluded       : {n_combo} ({combo_df['plant_species'].nunique()} kelas)")
    print(f"      Jumlah kelas tunggal    : {n_classes}")

    assert n_classes == 68, f"Expected 68 single-species classes, got {n_classes}"
    assert n_total_single == 49523, f"Expected 49,523 single-species images, got {n_total_single}"
    assert n_train == 37408, f"Expected 37,408 train images, got {n_train}"
    assert n_val == 6068, f"Expected 6,068 val images, got {n_val}"
    assert n_test == 6047, f"Expected 6,047 test images, got {n_test}"
    assert n_combo == 107, f"Expected 107 excluded combo images, got {n_combo}"

    # Verify consistency with label_mapping.yaml
    lm_valid_single_species = {
        e["plant_species"]
        for e in lm["label_mappings"]
        if e["task_eligibility"]["species_id"]
        and e["usage_status"] == "included"
        and " / " not in str(e["plant_species"])
    }
    manifest_species = set(single_df["plant_species"].unique())
    assert manifest_species == lm_valid_single_species, (
        f"Mismatch manifest vs label_mapping: {manifest_species ^ lm_valid_single_species}"
    )

    # Extract ONLY Stage 6 Train for 68 single-species (NEVER touch Val 6,068 or Locked Test 6,047)
    train_s68 = single_df[single_df["split_species_id"] == "train"].copy()
    assert train_s68["image_id"].nunique() == 37408
    assert not train_s68["plant_species"].astype(str).str.contains(" / ", regex=False).any()
    assert not (train_s68["plant_species"].astype(str).str.lower() == "unknown").any()
    assert not (train_s68["usage_status"].astype(str) == "quarantined").any()
    assert not (train_s68["split_species_id"] == "test").any()
    assert not (train_s68["split_species_id"] == "validation").any()

    # Build deterministic class mapping (0..67)
    sorted_classes = sorted(manifest_species)
    class_to_idx = {cls_name: idx for idx, cls_name in enumerate(sorted_classes)}
    idx_to_class = {str(idx): cls_name for idx, cls_name in enumerate(sorted_classes)}
    train_s68["class_idx"] = train_s68["plant_species"].map(class_to_idx)

    # Validate file paths on disk
    print(f"[3/6] Memvalidasi keberadaan 37.408 path gambar pada: {dataset_root}")
    missing_paths = []
    for rel_p in train_s68["relative_path"].astype(str):
        full_p = dataset_root / rel_p.replace("\\", "/")
        if not full_p.is_file():
            missing_paths.append(rel_p)
    print(f"      Path ditemukan: {len(train_s68) - len(missing_paths)} / {len(train_s68)} | Hilang: {len(missing_paths)}")
    if missing_paths:
        raise FileNotFoundError(f"Ditemukan {len(missing_paths)} file gambar hilang! Contoh: {missing_paths[:5]}")

    # Validate PIL readability on stratified/random sample
    sample_n = len(train_s68) if args.verify_pil_sample < 0 else min(args.verify_pil_sample, len(train_s68))
    corrupt_files = []
    if sample_n > 0:
        sample_df = train_s68.sample(n=sample_n, random_state=args.seed)
        for rel_p in sample_df["relative_path"].astype(str):
            full_p = dataset_root / rel_p.replace("\\", "/")
            try:
                with Image.open(full_p) as img:
                    img.convert("RGB")
            except Exception as exc:
                corrupt_files.append((rel_p, str(exc)))
        print(f"[4/6] Uji keterbacaan PIL ({sample_n} sampel acak): OK={sample_n - len(corrupt_files)}, Corrupt={len(corrupt_files)}")
        if corrupt_files:
            raise RuntimeError(f"Ditemukan gambar corrupt: {corrupt_files[:5]}")

    # Perform group-aware stratified split (~85% inner_train / ~15% inner_val)
    print(f"[5/6] Membagi Train Stage 6 (37.408 gambar) -> inner_train (~85%) & inner_val (~15%) berdasarkan meta_component_id (seed={args.seed})...")
    tr_groups, va_groups = greedy_stratified_group_split(
        train_s68,
        group_col="meta_component_id",
        label_col="plant_species",
        val_ratio=args.inner_val_ratio,
        seed=args.seed,
    )

    inner_train = train_s68[train_s68["meta_component_id"].astype(str).isin(tr_groups)].copy()
    inner_val = train_s68[train_s68["meta_component_id"].astype(str).isin(va_groups)].copy()

    # Strict anti-leakage and class coverage assertions
    overlap_mc = set(inner_train["meta_component_id"]) & set(inner_val["meta_component_id"])
    overlap_img = set(inner_train["image_id"]) & set(inner_val["image_id"])
    assert len(overlap_mc) == 0, f"LEAKAGE DETECTED: {len(overlap_mc)} meta_component_id overlap!"
    assert len(overlap_img) == 0, f"LEAKAGE DETECTED: {len(overlap_img)} image_id overlap!"
    assert len(inner_train) + len(inner_val) == 37408, "Row sum mismatch!"
    assert inner_train["plant_species"].nunique() == 68, f"inner_train missing classes: {68 - inner_train['plant_species'].nunique()}"
    assert inner_val["plant_species"].nunique() == 68, f"inner_val missing classes: {68 - inner_val['plant_species'].nunique()}"

    cols_to_save = [
        "image_id", "relative_path", "source_dataset", "plant_species", "class_idx",
        "parent_source_group_id", "meta_component_id", "split_species_id"
    ]
    inner_train[cols_to_save].to_csv(out_dir / "task1_inner_train.csv", index=False)
    inner_val[cols_to_save].to_csv(out_dir / "task1_inner_val.csv", index=False)

    with open(out_dir / "task1_class_mapping.json", "w", encoding="utf-8") as f:
        json.dump({"num_classes": 68, "class_to_idx": class_to_idx, "idx_to_class": idx_to_class}, f, indent=2, ensure_ascii=False)

    summary = {
        "stage": "8.1_task1_pilot",
        "seed": args.seed,
        "target_inner_val_ratio": args.inner_val_ratio,
        "num_classes": 68,
        "stage6_train_single_species_images": n_train,
        "stage6_train_meta_components": int(train_s68["meta_component_id"].nunique()),
        "inner_train_images": len(inner_train),
        "inner_train_ratio": round(len(inner_train) / n_train, 4),
        "inner_train_meta_components": int(inner_train["meta_component_id"].nunique()),
        "inner_train_classes": int(inner_train["plant_species"].nunique()),
        "inner_val_images": len(inner_val),
        "inner_val_ratio": round(len(inner_val) / n_train, 4),
        "inner_val_meta_components": int(inner_val["meta_component_id"].nunique()),
        "inner_val_classes": int(inner_val["plant_species"].nunique()),
        "meta_component_overlap": len(overlap_mc),
        "image_id_overlap": len(overlap_img),
        "stage6_validation_used": False,
        "locked_test_used": False,
        "missing_paths": len(missing_paths),
        "pil_sample_checked": sample_n,
        "pil_corrupt_found": len(corrupt_files),
    }
    with open(out_dir / "task1_pilot_split_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("[6/6] Selesai! Ringkasan split pilot Task 1:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
