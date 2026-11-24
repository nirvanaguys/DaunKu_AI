#!/usr/bin/env python3
"""
audit_879_leakage_pairs.py — DaunKu AI Stage 6 Phase 2: Audit 879 Potential Leakage Pairs
"""

import csv
import os
import re
from pathlib import Path
from collections import defaultdict, Counter
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "Dataset"
LEAK_PATH = PROJECT_ROOT / "reports" / "potential_data_leakage.csv"
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "canonical_manifest.csv"

def inspect_879_pairs():
    print("=" * 80)
    print("PHASE 2: AUDIT 879 POTENTIAL LEAKAGE PAIRS")
    print("=" * 80)

    # 1. Load manifest parent mapping
    file_to_parent = {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            file_to_parent[r["relative_path"].replace("\\", "/")] = r["parent_source_group_id"]

    # 2. Filter 879 pairs (diff parent)
    pairs_879 = []
    with open(LEAK_PATH, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            f1 = r["File 1"].replace("\\", "/")
            f2 = r["File 2"].replace("\\", "/")
            p1 = file_to_parent.get(f1)
            p2 = file_to_parent.get(f2)
            if p1 and p2 and p1 != p2:
                pairs_879.append(r)

    print(f"Total unmerged potential leakage pairs identified: {len(pairs_879)}")

    # 3. Analyze patterns among the 879 pairs
    by_cat = Counter(r["Leakage Category"] for r in pairs_879)
    by_risk = Counter(r["Risk Level"] for r in pairs_879)
    by_ds_pair = Counter(f"{r['Dataset 1']} <--> {r['Dataset 2']}" for r in pairs_879)

    print(f"\nBreakdown by Leakage Category:")
    for k, v in by_cat.most_common():
        print(f"  - {k}: {v}")

    print(f"\nBreakdown by Risk Level:")
    for k, v in by_risk.most_common():
        print(f"  - {k}: {v}")

    print(f"\nBreakdown by Dataset Pairs:")
    for k, v in by_ds_pair.most_common():
        print(f"  - {k}: {v}")

    # Inspect filenames & stems to see if they share root names
    shared_stem = 0
    diff_stem = 0
    for r in pairs_879:
        fn1 = Path(r["File 1"]).name
        fn2 = Path(r["File 2"]).name
        # clean roboflow
        stem1 = re.sub(r"_(jpg|jpeg|png|bmp)\.rf\.[0-9a-fA-F]+$", "", Path(fn1).stem, flags=re.IGNORECASE)
        stem2 = re.sub(r"_(jpg|jpeg|png|bmp)\.rf\.[0-9a-fA-F]+$", "", Path(fn2).stem, flags=re.IGNORECASE)
        if stem1.lower() == stem2.lower():
            shared_stem += 1
        else:
            diff_stem += 1

    print(f"\nFilename Stem Comparison:")
    print(f"  - Identical base stem: {shared_stem}")
    print(f"  - Different base stem: {diff_stem}")

    # 4. Detailed audit of pairs: Sample check of dimensions and perceptual similarity
    decisions = Counter()
    audit_results = []

    for r in pairs_879:
        leak_id = r["Leakage ID"]
        f1_rel = r["File 1"].replace("\\", "/")
        f2_rel = r["File 2"].replace("\\", "/")
        cat = r["Leakage Category"]
        risk = r["Risk Level"]
        
        m = re.search(r"dist=(\d+)", cat)
        dist = int(m.group(1)) if m else -1

        fn1 = Path(f1_rel).name
        fn2 = Path(f2_rel).name
        stem1 = re.sub(r"_(jpg|jpeg|png|bmp)\.rf\.[0-9a-fA-F]+$", "", Path(fn1).stem, flags=re.IGNORECASE)
        stem2 = re.sub(r"_(jpg|jpeg|png|bmp)\.rf\.[0-9a-fA-F]+$", "", Path(fn2).stem, flags=re.IGNORECASE)

        # Decision rules based on evidence:
        # dist = 0: confirmed_duplicate or likely_same_source
        if dist == 0:
            if stem1.lower() == stem2.lower():
                dec = "confirmed_duplicate"
                reason = "dHash distance = 0 dan nama dasar foto identik (salinan augmentasi/ekspor berulang)"
            else:
                dec = "likely_same_source"
                reason = "dHash distance = 0 meskipun nama file berbeda (duplikasi biner/visual identik)"
        elif dist == 1:
            if stem1.lower() == stem2.lower():
                dec = "confirmed_duplicate"
                reason = "dHash distance = 1 dan nama dasar foto identik (variasi kompresi minor dari foto sumber yang sama)"
            else:
                dec = "likely_same_source"
                reason = "dHash distance = 1 (kemiripan visual sangat tinggi, variasi kompresi JPEG)"
        elif dist in [2, 3]:
            if stem1.lower() == stem2.lower():
                dec = "likely_same_source"
                reason = f"dHash distance = {dist} dengan nama dasar identik (variasi augmentasi pencahayaan/rotasi Roboflow)"
            else:
                # Different base stem with dist 2 or 3
                # Bisa merupakan variasi kamera berturutan (burst mode) atau visual similarity daun sejenis
                dec = "visually_similar_not_duplicate" if dist == 3 else "uncertain"
                reason = f"dHash distance = {dist} pada nama file berbeda (kandidat near-duplicate perseptual/daun serupa)"
        else:
            dec = "uncertain"
            reason = "Metrik jarak tidak terdefinisi"

        decisions[dec] += 1
        audit_results.append({
            "Leakage ID": leak_id,
            "File 1": f1_rel,
            "File 2": f2_rel,
            "Dataset 1": r["Dataset 1"],
            "Dataset 2": r["Dataset 2"],
            "dHash Distance": dist,
            "Risk Level": risk,
            "Decision": dec,
            "Evidence & Reasoning": reason
        })

    print(f"\nDecision Summary on 879 Pairs:")
    for k, v in decisions.most_common():
        print(f"  - {k}: {v} ({v/len(pairs_879)*100:.2f}%)")

    # Save audit CSV
    out_csv = PROJECT_ROOT / "reports" / "audit_879_leakage_decisions.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Leakage ID", "File 1", "File 2", "Dataset 1", "Dataset 2",
            "dHash Distance", "Risk Level", "Decision", "Evidence & Reasoning"
        ], lineterminator="\n")
        writer.writeheader()
        writer.writerows(audit_results)
    print(f"\nTersimpan rincian keputusan audit di: {out_csv}")

    # Connected Components analysis for conservative constraint merging
    # Build graph where nodes are parent_source_group_id
    from collections import defaultdict
    adj = defaultdict(set)
    for r in pairs_879:
        f1 = r["File 1"].replace("\\", "/")
        f2 = r["File 2"].replace("\\", "/")
        p1 = file_to_parent.get(f1)
        p2 = file_to_parent.get(f2)
        if p1 and p2 and p1 != p2:
            adj[p1].add(p2)
            adj[p2].add(p1)

    # Find connected components
    visited = set()
    components = []
    for node in list(adj.keys()):
        if node not in visited:
            comp = []
            queue = [node]
            visited.add(node)
            for curr in queue:
                comp.append(curr)
                for nxt in adj[curr]:
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
            components.append(comp)

    print(f"\nConnected Components Analysis (Graph of Connected Parent Groups):")
    print(f"  - Total parent groups terlibat: {len(visited):,}")
    print(f"  - Total connected components: {len(components):,}")
    comp_sizes = [len(c) for c in components]
    print(f"  - Ukuran component: min={min(comp_sizes)}, max={max(comp_sizes)}, mean={sum(comp_sizes)/len(comp_sizes):.2f}")
    large_comps = [c for c in components if len(c) > 5]
    print(f"  - Component dengan >5 parent groups: {len(large_comps)}")

    return {
        "pairs_879": pairs_879,
        "decisions": decisions,
        "audit_results": audit_results,
        "components": components,
        "parent_nodes_involved": len(visited)
    }

if __name__ == "__main__":
    inspect_879_pairs()
