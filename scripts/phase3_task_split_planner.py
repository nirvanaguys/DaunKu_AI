#!/usr/bin/env python3
"""
phase3_task_split_planner.py — DaunKu AI Stage 6 Phase 3 & 4: Task-Specific Split Strategy
"""

import csv
import random
import json
import yaml
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "canonical_manifest.csv"
LEAK_PATH = PROJECT_ROOT / "reports" / "potential_data_leakage.csv"

def design_task_splits():
    print("=" * 80)
    print("PHASE 3 & 4: TASK-SPECIFIC GROUP-AWARE SPLIT DESIGN")
    print("=" * 80)

    # 1. Load canonical manifest
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest_rows = list(csv.DictReader(f))

    print(f"Loaded {len(manifest_rows):,} manifest rows.")

    # 2. Build Connected Components of parent groups incorporating the 879 leakage pairs
    # Node: parent_source_group_id
    file_to_parent = {}
    for r in manifest_rows:
        file_to_parent[r["relative_path"].replace("\\", "/")] = r["parent_source_group_id"]

    parent_adj = defaultdict(set)
    leakage_constraints_count = 0
    with open(LEAK_PATH, "r", encoding="utf-8") as lf:
        for r in csv.DictReader(lf):
            f1 = r["File 1"].replace("\\", "/")
            f2 = r["File 2"].replace("\\", "/")
            p1 = file_to_parent.get(f1)
            p2 = file_to_parent.get(f2)
            if p1 and p2 and p1 != p2:
                parent_adj[p1].add(p2)
                parent_adj[p2].add(p1)
                leakage_constraints_count += 1

    print(f"Applied {leakage_constraints_count:,} pairwise near-duplicate constraints.")

    # Disjoint Set Union / BFS for components
    parent_to_comp = {}
    visited = set()
    comp_counter = 0

    all_parents = set(r["parent_source_group_id"] for r in manifest_rows)
    for p in all_parents:
        if p not in visited:
            comp_counter += 1
            comp_id = f"COMP_{comp_counter:05d}"
            queue = [p]
            visited.add(p)
            for curr in queue:
                parent_to_comp[curr] = comp_id
                for nxt in parent_adj[curr]:
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)

    print(f"Total unique parent groups: {len(all_parents):,}")
    print(f"Total merged meta-components (Group-Aware + Leakage Protected): {comp_counter:,}")

    # Map each image row to its meta-component
    for r in manifest_rows:
        r["meta_component_id"] = parent_to_comp[r["parent_source_group_id"]]

    # 3. Tasks definition and eligibility
    tasks = {
        "species_id": {
            "name": "Plant Species Identification",
            "elig_col": "eligible_species_id",
            "label_col": "plant_species",
            "target_ratio": (0.75, 0.125, 0.125)
        },
        "condition": {
            "name": "Plant Condition Classification",
            "elig_col": "eligible_condition",
            "label_col": "plant_condition",
            "target_ratio": (0.70, 0.15, 0.15)
        },
        "disease_diagnosis": {
            "name": "Disease/Symptom Diagnosis",
            "elig_col": "eligible_disease_diagnosis",
            "label_col": "disease_or_symptom",
            "target_ratio": (0.70, 0.15, 0.15)
        },
        "leaf_detection": {
            "name": "Leaf/Object Detection (Bounding Box)",
            "elig_col": "eligible_leaf_detection",
            "label_col": "canonical_label",
            "target_ratio": (0.75, 0.125, 0.125)
        }
    }

    task_splits = {}
    SEED = 42

    for task_key, tcfg in tasks.items():
        print(f"\nProcessing Task: {tcfg['name']} ({task_key})...")
        elig_col = tcfg["elig_col"]
        label_col = tcfg["label_col"]
        train_r, val_r, test_r = tcfg["target_ratio"]

        # Filter eligible rows
        eligible_rows = [r for r in manifest_rows if r[elig_col] == "True" and r["usage_status"] != "quarantined" and r["usage_status"] != "natural_background_holdout"]
        print(f"  Eligible Rows: {len(eligible_rows):,}")

        # Group rows by meta_component_id
        comp_rows = defaultdict(list)
        comp_labels = defaultdict(Counter)
        for r in eligible_rows:
            cid = r["meta_component_id"]
            comp_rows[cid].append(r)
            comp_labels[cid][r[label_col]] += 1

        print(f"  Eligible Meta-Components: {len(comp_rows):,}")

        # Assign primary label to each meta_component (majority vote)
        class_to_comps = defaultdict(list)
        for cid, rows in comp_rows.items():
            primary_lbl = comp_labels[cid].most_common(1)[0][0]
            class_to_comps[primary_lbl].append((cid, rows))

        print(f"  Total Classes: {len(class_to_comps)}")

        # Split components per class
        rng = random.Random(SEED)
        split_assignment = {} # comp_id -> split
        class_distribution = {
            "train": Counter(),
            "validation": Counter(),
            "test": Counter()
        }

        rare_classes = []
        for lbl, comps in sorted(class_to_comps.items()):
            # Sort components deterministically then shuffle
            comps.sort(key=lambda x: x[0])
            rng.shuffle(comps)

            n = len(comps)
            if n == 1:
                # Only 1 group: cannot split across train/val/test without leaking
                # Assign to train, document as rare class
                split_assignment[comps[0][0]] = "train"
                for r in comps[0][1]:
                    class_distribution["train"][r[label_col]] += 1
                rare_classes.append((lbl, n, len(comps[0][1])))
            elif n == 2:
                # 2 groups: 1 train, 1 test
                split_assignment[comps[0][0]] = "train"
                split_assignment[comps[1][0]] = "test"
                for r in comps[0][1]:
                    class_distribution["train"][r[label_col]] += 1
                for r in comps[1][1]:
                    class_distribution["test"][r[label_col]] += 1
            else:
                # >= 3 groups: allocate based on target ratio
                n_test = max(1, round(n * test_r))
                n_val = max(1, round(n * val_r))
                # Ensure train has at least 1
                if n_test + n_val >= n:
                    n_val = 1
                    n_test = 1
                n_train = n - n_val - n_test

                train_comps = comps[:n_train]
                val_comps = comps[n_train:n_train + n_val]
                test_comps = comps[n_train + n_val:]

                for c in train_comps:
                    split_assignment[c[0]] = "train"
                    for r in c[1]:
                        class_distribution["train"][r[label_col]] += 1
                for c in val_comps:
                    split_assignment[c[0]] = "validation"
                    for r in c[1]:
                        class_distribution["validation"][r[label_col]] += 1
                for c in test_comps:
                    split_assignment[c[0]] = "test"
                    for r in c[1]:
                        class_distribution["test"][r[label_col]] += 1

        # Summary of splits for this task
        split_counts = Counter(split_assignment.values())
        img_counts = {
            sp: sum(class_distribution[sp].values()) for sp in ["train", "validation", "test"]
        }
        total_imgs = sum(img_counts.values())

        print(f"  Split Components: Train={split_counts['train']:,}, Val={split_counts['validation']:,}, Test={split_counts['test']:,}")
        print(f"  Split Images: Train={img_counts['train']:,} ({img_counts['train']/total_imgs*100:.1f}%), Val={img_counts['validation']:,} ({img_counts['validation']/total_imgs*100:.1f}%), Test={img_counts['test']:,} ({img_counts['test']/total_imgs*100:.1f}%)")
        print(f"  Rare Classes (<3 groups): {len(rare_classes)}")

        task_splits[task_key] = {
            "split_assignment": split_assignment,
            "class_distribution": class_distribution,
            "img_counts": img_counts,
            "comp_counts": split_counts,
            "rare_classes": rare_classes
        }

    return task_splits, manifest_rows, parent_to_comp

if __name__ == "__main__":
    design_task_splits()
