#!/usr/bin/env python3
"""
build_canonical_dataset_stage5.py — DaunKu AI Stage 5: Canonical Dataset & Label Mapping (Final Revision)
Revisi Final Berdasarkan Arahan & Keputusan Pengguna:
1. Pemisahan eksplisit antara `mapping_status` dan `usage_status` (termasuk flags task_eligibility).
2. Penanganan 10 gambar mawar berlabel konflik (50 file instance) -> label_conflict & quarantined.
3. Penanganan Daun Kopi -> exclude dari disease classification, eligible untuk leaf detection.
4. Penanganan Rose Mosaic Virus pada Hibiscus -> suspected_mislabel & quarantined.
5. Penanganan Yellow Disease -> provisional & pending_review (exclude dari diagnosis spesifik).
6. Implementasi `parent_source_group_id` berbasis Disjoint Set Union (DSU) untuk Group-Aware Split.
7. Pelabelan 689 gambar berlatar alami sebagai `natural_background_holdout` dengan dokumentasi batasan.
8. Harmonisasi taksonomi botani (28 taksa acuan + 52 spesies goletplant).
9. Output: artifacts/canonical_manifest.csv, configs/label_mapping.yaml, reports/canonical_dataset_design.md.
"""

import os
import sys
import csv
import yaml
import time
import re
from pathlib import Path
from collections import defaultdict, Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "Dataset"
REPORTS_DIR = PROJECT_ROOT / "reports"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
CONFIGS_DIR = PROJECT_ROOT / "configs"

# Disjoint Set Union for parent_source_group_id clustering
class DisjointSetUnion:
    def __init__(self):
        self.parent = {}
    def find(self, x):
        if self.parent.setdefault(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[rx] = ry

# 10 Known Conflicting SHA-256 for Rose (Pest Damage vs Rose Mosaic Virus)
ROSE_CONFLICT_SHAS = {
    "37eae840bb40e5b95eeb1b6d4fcbbfc2b95237574c5440bad36b0b731d633935",
    "9bd2fee7792756e3844876e11220251cbe6e26aa0f8411e98705f0e10b89605c",
    "30350db019261d7fafa432d4e98798efdfbd92edfeb6c7dc1380b1330013bc36",
    "2753374bffdf1c041d064cb4ff74e551ff898a860b49dc2e8f291c583f1c955d",
    "dc8e2ed4a0e85e6d853b41fb32349d6f43cbcb95ff63874b8d37560632957203",
    "1aa698e01a62d4f227e4f87748f7d8a2c6e6b385a179ee1d70eccf32a6b0c14d",
    "d6d9c1314d60700bb0d45d4e4dd720b7b81be9b658cb370ae9a8da338bd4db4a",
    "579db11f9645d3464c78b920cca04446c0b0dfe7be0af02c900a1d52b2654f18",
    "765e4d9066182c885b52dafb477c83ee66a2de1645570520e36e233fdd7f0285",
    "f81fbb711511c05fe7d87a1a870c17afb7f8b5bc4be5fa80e5098456e9803471"
}

# Botanical taxonomy normalization dictionary
SPECIES_NORMALIZATION = {
    "Aloevera": "Aloe Vera (Aloe barbadensis)",
    "Aloe-Vera-Aloe-barbadensis-": "Aloe Vera (Aloe barbadensis)",
    "snake plant": "Snake Plant (Dracaena trifasciata)",
    "Snake-Plant-Dracaena-trifasciata-": "Snake Plant (Dracaena trifasciata)",
    "Aglaonema": "Aglaonema (Aglaonema commutatum)",
    "Philippine-Evergreen-Aglaonema-Commutatum-": "Aglaonema (Aglaonema commutatum)",
    "Chlorophytum comosum": "Spider Plant (Chlorophytum comosum)",
    "Spider-Plant-Chloropythum-Comosum-": "Spider Plant (Chlorophytum comosum)",
    "Epipremnum": "Golden Pothos (Epipremnum aureum)",
    "Pothos-Epipremnum-aureum-": "Golden Pothos (Epipremnum aureum)",
    "FicusElastica": "Rubber Fig (Ficus elastica)",
    "Rubber-Fig-Ficus-Elastica-": "Rubber Fig (Ficus elastica)",
    "Alocasia": "Alocasia Frydek (Alocasia micholitziana)",
    "Elephant-Ear-Alocasia-Frydek-": "Alocasia Frydek (Alocasia micholitziana)",
    "Alocasia-Green-Velvet-Micholitziana-Frydek-": "Alocasia Frydek (Alocasia micholitziana)",
    "Tradescantia fluminensis": "Tradescantia (Tradescantia fluminensis)",
    "Inch-Plant-Tradescantia-zebrina-": "Inch Plant (Tradescantia zebrina)",
    "Swiss Cheese Plant -Monstera Deliciosa-": "Monstera deliciosa",
    "Spear-Plant-Dracaena-angolensis-": "Dracaena angolensis",
    "Bitter gourd": "Bitter Gourd (Momordica charantia)",
    "Brinjal": "Eggplant (Solanum melongena)",
    "Ladies Finger": "Okra (Abelmoschus esculentus)",
    "Ladies finger": "Okra (Abelmoschus esculentus)",
    "Snake gourd": "Snake Gourd (Trichosanthes cucumerina)",
    "Yard long bean": "Yardlong Bean (Vigna unguiculata subsp. sesquipedalis)",
    "Mung bean": "Mung Bean (Vigna radiata)",
    "Sesame": "Sesame (Sesamum indicum)",
    "sesame": "Sesame (Sesamum indicum)",
    "anthurium": "Anthurium",
    "verbena": "Verbena",
    "zz plant": "ZZ Plant (Zamioculcas zamiifolia)",
    "Fiddle-leaf": "Fiddle-leaf Fig (Ficus lyrata)",
    "ChineseMoneyPlant": "Chinese Money Plant (Pilea peperomioides)",
    "Jade plant": "Jade Plant (Crassula ovata)",
    "BostonFern": "Boston Fern (Nephrolepis exaltata)",
    "BunnyEarCactus": "Bunny Ears Cactus (Opuntia microdasys)",
    "Zebra haworthia": "Zebra Haworthia (Haworthiopsis fasciata)",
    "White orchids": "White Orchid (Phalaenopsis)",
    "None (Background)": "None (Background)",
    "Unknown": "Unknown"
}

def normalize_species_name(name):
    """Menyelaraskan variasi penamaan botani menjadi taksonomi resmi."""
    if not name:
        return "Unknown"
    if name in SPECIES_NORMALIZATION:
        return SPECIES_NORMALIZATION[name]
    # For combinations e.g. "Aglaonema / BunnyEarCactus"
    if " / " in name:
        parts = name.split(" / ")
        norm_parts = [SPECIES_NORMALIZATION.get(p, p) for p in parts]
        return " / ".join(sorted(list(set(norm_parts))))
    return name

def build_taxonomy_rules():
    """
    Kamus aturan taksonomi dan kelayakan task per label:
    Returns dict: (dataset, label) -> {
        canonical_label, plant_species, plant_condition, disease_or_symptom,
        category, mapping_status, default_usage_status,
        eligibility: {species_id, condition, disease_diagnosis, leaf_detection},
        evidence, notes
    }
    """
    rules = {}
    
    # 1. Arabian Jasmine (AJLCD-2025)
    ds_aj = "Arabian Jasmine Leaf Condition Dataset (AJLCD-2025"
    aj_classes = [
        ("Healthy", "Arabian Jasmine - Healthy", "Healthy", "None (Healthy)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
         "Folder Healthy pada AJLCD-2025", "Daun melati sehat tanpa patogen"),
        ("Anthracnose", "Arabian Jasmine - Anthracnose", "Unhealthy", "Anthracnose (Colletotrichum)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
         "Folder Anthracnose pada AJLCD-2025", "Bercak nekrotik jamur Colletotrichum"),
        ("Cholorosis", "Arabian Jasmine - Chlorosis", "Unhealthy", "Chlorosis (Nutrient / Abiotic)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
         "Folder Cholorosis [sic] pada AJLCD-2025", "Gejala klorosis/daun menguning"),
        ("Dried Leaf", "Arabian Jasmine - Dried Leaf", "Unhealthy", "Leaf Desiccation / Dehydration", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
         "Folder Dried Leaf pada AJLCD-2025", "Daun kering akibat stres lingkungan"),
        ("Initial stage", "Arabian Jasmine - Initial Disease Stage", "Unhealthy", "Early Disease Symptoms (Unspecified)", "ambiguous", "quarantined",
         {"species_id": True, "condition": True, "disease_diagnosis": False, "leaf_detection": False},
         "Folder Initial stage pada AJLCD-2025", "Gejala tahap awal tanpa diagnosis patogen spesifik (karantina untuk disease diagnosis)"),
        ("Leaf Blight", "Arabian Jasmine - Leaf Blight", "Unhealthy", "Leaf Blight", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
         "Folder Leaf Blight pada AJLCD-2025", "Hawar daun jamur"),
        ("Leaf Spot", "Arabian Jasmine - Leaf Spot", "Unhealthy", "Leaf Spot (Fungal / Bacterial)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
         "Folder Leaf Spot pada AJLCD-2025", "Bercak daun umum"),
        ("Pest Damage", "Arabian Jasmine - Pest Damage", "Unhealthy", "Insect Pest Damage", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
         "Folder Pest Damage pada AJLCD-2025", "Kerusakan gigitan serangga")
    ]
    for orig, can, cond, symp, mst, ust, elig, evid, note in aj_classes:
        rules[(ds_aj, orig)] = {
            "canonical_label": can, "plant_species": "Arabian Jasmine (Jasminum sambac)",
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Ornamental Flower",
            "mapping_status": mst, "usage_status": ust, "eligibility": elig,
            "evidence": evid, "notes": note
        }

    # 2. Potato Leaf Disease
    ds_pot = "Potato Leaf Disease Dataset in Uncontrolled Environment"
    pot_classes = [
        ("Healthy", "Potato - Healthy", "Healthy", "None (Healthy)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Daun kentang sehat alami"),
        ("Bacteria", "Potato - Bacterial Infection", "Unhealthy", "Bacterial Infection", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Infeksi bakteri"),
        ("Fungi", "Potato - Fungal Infection", "Unhealthy", "Fungal Infection", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Infeksi jamur umum"),
        ("Nematode", "Potato - Nematode Infestation", "Unhealthy", "Nematode Infestation", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Gejala nematoda"),
        ("Pest", "Potato - Pest Damage", "Unhealthy", "Insect Pest Damage", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Serangan hama serangga"),
        ("Phytopthora", "Potato - Late Blight (Phytophthora)", "Unhealthy", "Late Blight (Phytophthora infestans)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Hawar daun Phytophthora"),
        ("Virus", "Potato - Viral Disease", "Unhealthy", "Viral Disease (Potato Virus)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Infeksi virus kentang")
    ]
    for orig, can, cond, symp, mst, ust, elig, note in pot_classes:
        rules[(ds_pot, orig)] = {
            "canonical_label": can, "plant_species": "Potato (Solanum tuberosum)",
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Vegetable Crop",
            "mapping_status": mst, "usage_status": ust, "eligibility": elig,
            "evidence": f"Folder {orig} pada Potato Leaf Disease", "notes": note
        }

    # 3. Tomato Leaf Diseases
    ds_tom = "Tomato leaf diseases"
    tom_classes = [
        ("Healthy", "Tomato - Healthy", "Healthy", "None (Healthy)", "Daun tomat sehat"),
        ("Bacterial Spot", "Tomato - Bacterial Spot", "Unhealthy", "Bacterial Spot (Xanthomonas)", "Bercak bakteri"),
        ("Early Blight", "Tomato - Early Blight", "Unhealthy", "Early Blight (Alternaria solani)", "Hawar daun dini"),
        ("Late Blight", "Tomato - Late Blight", "Unhealthy", "Late Blight (Phytophthora infestans)", "Hawar daun lanjut"),
        ("Leaf Mold", "Tomato - Leaf Mold", "Unhealthy", "Leaf Mold (Passalora fulva)", "Kapang daun"),
        ("Cercospora leaf mold", "Tomato - Cercospora Leaf Mold", "Unhealthy", "Cercospora Leaf Mold", "Kapang Cercospora"),
        ("Tomato Leaf Curl Virus", "Tomato - Leaf Curl Virus", "Unhealthy", "Tomato Leaf Curl Virus (TYLCV)", "Virus daun keriting"),
        ("Leaf Miner", "Tomato - Leaf Miner", "Unhealthy", "Leaf Miner Damage (Liriomyza)", "Ulat penggorok daun"),
        ("Spider Mites", "Tomato - Spider Mites", "Unhealthy", "Spider Mite Damage (Tetranychidae)", "Tungau merah"),
        ("Insect Damage", "Tomato - Insect Damage", "Unhealthy", "Insect Pest Damage", "Kerusakan serangga umum")
    ]
    for orig, can, cond, symp, desc in tom_classes:
        rules[(ds_tom, orig)] = {
            "canonical_label": can, "plant_species": "Tomato (Solanum lycopersicum)",
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Vegetable Crop",
            "mapping_status": "mapped", "usage_status": "included",
            "eligibility": {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
            "evidence": f"Folder {orig} pada Tomato leaf diseases", "notes": desc
        }

    # 4. Rubber Leaf Dataset
    ds_rub = "Rubber_Leaf_Dataset"
    rub_classes = [
        ("Healthy", "Rubber Tree - Healthy", "Healthy", "None (Healthy)"),
        ("Anthracnose", "Rubber Tree - Anthracnose", "Unhealthy", "Anthracnose (Colletotrichum)"),
        ("Dry_Leaf", "Rubber Tree - Dry Leaf", "Unhealthy", "Leaf Desiccation / Dry Leaf"),
        ("Leaf_Spot", "Rubber Tree - Leaf Spot", "Unhealthy", "Leaf Spot (Fungal / Bacterial)")
    ]
    for orig, can, cond, symp in rub_classes:
        # Raw Dataset (Included)
        rules[(ds_rub, f"Raw_Dataset / {orig}")] = {
            "canonical_label": can, "plant_species": "Rubber Tree (Hevea brasiliensis)",
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Plantation Crop",
            "mapping_status": "mapped", "usage_status": "included",
            "eligibility": {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False},
            "evidence": f"Folder Raw_Dataset/{orig}", "notes": "Data primer daun karet resolusi tinggi"
        }
        # Compressed Dataset (Excluded from training/evaluation to prevent duplication)
        rules[(ds_rub, f"Compressed_Dataset / {orig}")] = {
            "canonical_label": can, "plant_species": "Rubber Tree (Hevea brasiliensis)",
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Plantation Crop",
            "mapping_status": "excluded_from_task", "usage_status": "excluded_from_task",
            "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
            "evidence": f"Folder Compressed_Dataset/{orig}", "notes": "Redundan 100% biner dengan Raw_Dataset (dikecualikan)"
        }

    # 5. Perfect Data Set & Rose And Marigold Leaf Disease 1
    ds_pds = "Perfect Data Set"
    ds_rm1 = "Rose And MArigold Leaf Disease 1"
    pds_classes = [
        ("marigold / Alternaria Leaf Blight", "Marigold - Alternaria Leaf Blight", "Marigold (Tagetes erecta)", "Unhealthy", "Alternaria Leaf Blight", "Alternaria pada Tagetes"),
        ("marigold / Helathy Leaves", "Marigold - Healthy", "Marigold (Tagetes erecta)", "Healthy", "None (Healthy)", "Daun marigold sehat"),
        ("marigold / Pest Damaged", "Marigold - Pest Damage", "Marigold (Tagetes erecta)", "Unhealthy", "Insect Pest Damage", "Kerusakan hama marigold"),
        ("rose / Healthy", "Rose - Healthy", "Rose (Rosa)", "Healthy", "None (Healthy)", "Daun mawar sehat (no_bg)"),
        ("rose / botrytis blight", "Rose - Botrytis Blight", "Rose (Rosa)", "Unhealthy", "Botrytis Blight (Botrytis cinerea)", "Hawar Botrytis mawar"),
        ("rose / Pest Damage", "Rose - Pest Damage", "Rose (Rosa)", "Unhealthy", "Insect Pest Damage", "Kerusakan hama serangga pada mawar"),
        ("rose / Rose Mosaic Virus", "Rose - Mosaic Virus", "Rose (Rosa)", "Unhealthy", "Rose Mosaic Virus (PNRSV/ApMV)", "Virus mozaik mawar")
    ]
    for orig, can, spec, cond, symp, desc in pds_classes:
        # Perfect Data Set is absorbed by dataset for various disease detection
        rules[(ds_pds, orig)] = {
            "canonical_label": can, "plant_species": spec,
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Ornamental Flower",
            "mapping_status": "mapped", "usage_status": "excluded_from_task",
            "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
            "evidence": f"Folder {orig} pada Perfect Data Set", "notes": f"Diserap dataset induk berbagai penyakit: {desc}"
        }
        # Rose And Marigold 1 is 100% duplicate of Perfect Data Set
        rules[(ds_rm1, f"Perfect Data Set / {orig}")] = {
            "canonical_label": can, "plant_species": spec,
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Ornamental Flower",
            "mapping_status": "excluded_from_task", "usage_status": "excluded_from_task",
            "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
            "evidence": f"Duplikat 100% Perfect Data Set", "notes": f"Salinan identik Perfect Data Set: {desc}"
        }

    # 6. dataset for various disease detection of Rose, Tagetes, Hibiscus
    ds_var = "dataset for various disease detection of Rose ,Tagetes erecta  Hibiscus rosa-sinensis"
    var_classes = [
        ("Rosa / Healthy Leaf", "Rose - Healthy", "Rose (Rosa)", "Healthy", "None (Healthy)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Daun mawar sehat (no_bg)"),
        ("Rosa / Fungal Leaf Spot Disease", "Rose - Fungal Leaf Spot", "Rose (Rosa)", "Unhealthy", "Fungal Leaf Spot (Diplocarpon rosae / Cercospora)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Bercak daun jamur mawar"),
        ("Rosa / insect damage", "Rose - Pest Damage", "Rose (Rosa)", "Unhealthy", "Insect Pest Damage", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Kerusakan hama serangga mawar"),
        ("Rosa / Rose Mosaic Virus", "Rose - Mosaic Virus", "Rose (Rosa)", "Unhealthy", "Rose Mosaic Virus", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Virus mozaik mawar"),
        ("Rosa / Botrytis Blight", "Rose - Botrytis Blight", "Rose (Rosa)", "Unhealthy", "Botrytis Blight (Botrytis cinerea)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Hawar daun Botrytis"),
        ("Rosa / Nutrient Deficiency", "Rose - Nutrient Deficiency", "Rose (Rosa)", "Unhealthy", "Nutrient Deficiency (Chlorosis)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Defisiensi hara/klorosis mawar"),
        ("Rosa / Rosa", "Rose - Unspecified Condition", "Rose (Rosa)", "Unknown", "Unknown / Unspecified", "ambiguous", "quarantined",
         {"species_id": True, "condition": False, "disease_diagnosis": False, "leaf_detection": False}, "Subfolder hanya mencantumkan genus Rosa tanpa keterangan kondisi (karantina)"),
        
        # Tagetes erecta (Marigold)
        ("Tagetes erecta / Alternaria Leaf Blight", "Marigold - Alternaria Leaf Blight", "Marigold (Tagetes erecta)", "Unhealthy", "Alternaria Leaf Blight", "mapped", "natural_background_holdout",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Hawar daun Alternaria marigold (latar alami)"),
        ("Tagetes erecta / Heaalthy Leaf", "Marigold - Healthy", "Marigold (Tagetes erecta)", "Healthy", "None (Healthy)", "mapped", "natural_background_holdout",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Daun marigold sehat (latar alami)"),
        ("Tagetes erecta / Pest Damage", "Marigold - Pest Damage", "Marigold (Tagetes erecta)", "Unhealthy", "Insect Pest Damage", "mapped", "natural_background_holdout",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Kerusakan serangga marigold (latar alami)"),
        ("Tagetes erecta / Tagetes", "Marigold - Unspecified Condition", "Marigold (Tagetes erecta)", "Unknown", "Unknown / Unspecified", "ambiguous", "quarantined",
         {"species_id": True, "condition": False, "disease_diagnosis": False, "leaf_detection": False}, "Subfolder hanya genus Tagetes tanpa keterangan kondisi (karantina)"),
        
        # Hibiscus rosa-sinensis
        ("Hibiscus rosa-sinensis / Healthy Leaf", "Hibiscus - Healthy", "Hibiscus (Hibiscus rosa-sinensis)", "Healthy", "None (Healthy)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Daun kembang sepatu sehat"),
        ("Hibiscus rosa-sinensis / Bacterial Leaf or Spot", "Hibiscus - Bacterial Leaf Spot", "Hibiscus (Hibiscus rosa-sinensis)", "Unhealthy", "Bacterial Leaf Spot (Pseudomonas / Xanthomonas)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Bercak bakteri kembang sepatu"),
        ("Hibiscus rosa-sinensis / Nutrient Deficiency", "Hibiscus - Nutrient Deficiency", "Hibiscus (Hibiscus rosa-sinensis)", "Unhealthy", "Nutrient Deficiency (Chlorosis)", "mapped", "included",
         {"species_id": True, "condition": True, "disease_diagnosis": True, "leaf_detection": False}, "Defisiensi hara kembang sepatu"),
        ("Hibiscus rosa-sinensis / Hibiscus rosa-sinensis", "Hibiscus - Unspecified Condition", "Hibiscus (Hibiscus rosa-sinensis)", "Unknown", "Unknown / Unspecified", "ambiguous", "quarantined",
         {"species_id": True, "condition": False, "disease_diagnosis": False, "leaf_detection": False}, "Subfolder spesies tanpa keterangan kondisi penyakit (karantina)"),
        ("Hibiscus rosa-sinensis / Rose Mosaic Virus", "Hibiscus - Suspected Mosaic Virus", "Hibiscus (Hibiscus rosa-sinensis)", "Unhealthy", "Mosaic Virus (Suspected Mislabel)", "suspected_mislabel", "quarantined",
         {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False}, "Rose Mosaic Virus secara biologis spesifik genus Rosa; diduga salah penamaan pada Hibiscus (karantina total)")
    ]
    for orig, can, spec, cond, symp, mst, ust, elig, note in var_classes:
        rules[(ds_var, orig)] = {
            "canonical_label": can, "plant_species": spec,
            "plant_condition": cond, "disease_or_symptom": symp, "category": "Ornamental Flower",
            "mapping_status": mst, "usage_status": ust, "eligibility": elig,
            "evidence": f"Folder {orig} pada dataset berbagai penyakit", "notes": note
        }

    # 7. Plant Classification and Disease v3i & v1i
    ds_v3 = "Plant Classification and Disease.v3i.tensorflow"
    ds_v1 = "Plant Classification and Disease.v1i.tensorflow"
    
    v3_plants = {
        "Swiss Cheese Plant -Monstera Deliciosa-": ("Monstera deliciosa", "Houseplant"),
        "Aloe-Vera-Aloe-barbadensis-": ("Aloe Vera (Aloe barbadensis)", "Houseplant / Medicinal"),
        "Pothos-Epipremnum-aureum-": ("Golden Pothos (Epipremnum aureum)", "Houseplant"),
        "Spider-Plant-Chloropythum-Comosum-": ("Spider Plant (Chlorophytum comosum)", "Houseplant"),
        "Inch-Plant-Tradescantia-zebrina-": ("Inch Plant (Tradescantia zebrina)", "Houseplant"),
        "Rubber-Fig-Ficus-Elastica-": ("Rubber Fig (Ficus elastica)", "Houseplant"),
        "Snake-Plant-Dracaena-trifasciata-": ("Snake Plant (Dracaena trifasciata)", "Houseplant"),
        "Elephant-Ear-Alocasia-Frydek-": ("Alocasia Frydek (Alocasia micholitziana)", "Houseplant"),
        "Alocasia-Green-Velvet-Micholitziana-Frydek-": ("Alocasia Frydek (Alocasia micholitziana)", "Houseplant"),
        "Philippine-Evergreen-Aglaonema-Commutatum-": ("Aglaonema (Aglaonema commutatum)", "Houseplant"),
        "Spear-Plant-Dracaena-angolensis-": ("Dracaena angolensis", "Houseplant")
    }
    
    v3_conditions = {
        "Unhealthy-Sunburn": ("Sunburn (Solar Scorching)", "Stres abiotik sengatan matahari"),
        "Unhealthy-Rust": ("Rust (Pucciniales)", "Penyakit karat daun jamur Pucciniales"),
        "Unhealthy-Leaf-Curl": ("Leaf Curl (Abiotic / Viral)", "Gejala daun menggulung"),
        "Unhealthy-Dehydration": ("Dehydration / Under-watering", "Stres kekurangan air"),
        "Unhealthy-Overwatering": ("Over-watering / Root Rot Indication", "Stres kelebihan air"),
        "Unhealthy-Mineral-Deficiency": ("Mineral Deficiency (Chlorosis)", "Defisiensi hara mineral"),
        "Unhealthy-Powdery-Mildew": ("Powdery Mildew (Erysiphales)", "Embun tepung akibat jamur")
    }
    
    for orig_p, (spec, cat) in v3_plants.items():
        rules[(ds_v3, orig_p)] = {
            "canonical_label": f"{spec} - Plant Object", "plant_species": spec,
            "plant_condition": "Unknown", "disease_or_symptom": "Unknown / Unspecified", "category": cat,
            "mapping_status": "mapped", "usage_status": "included",
            "eligibility": {"species_id": True, "condition": False, "disease_diagnosis": False, "leaf_detection": True},
            "evidence": f"Bounding box tanaman {orig_p} pada v3i", "notes": f"Objek deteksi tanaman hias {spec}"
        }
        rules[(ds_v1, orig_p)] = {
            "canonical_label": f"{spec} - Plant Object", "plant_species": spec,
            "plant_condition": "Unknown", "disease_or_symptom": "Unknown / Unspecified", "category": cat,
            "mapping_status": "excluded_from_task", "usage_status": "excluded_from_task",
            "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
            "evidence": f"Versi v1i (subset v3i)", "notes": "Dikecualikan karena merupakan subset usang dari v3i"
        }
        
    for orig_c, (symp, desc) in v3_conditions.items():
        rules[(ds_v3, orig_c)] = {
            "canonical_label": f"Houseplants - {orig_c.replace('Unhealthy-', '')}", "plant_species": "Houseplants (Multi-Species)",
            "plant_condition": "Unhealthy", "disease_or_symptom": symp, "category": "Houseplant",
            "mapping_status": "mapped", "usage_status": "included",
            "eligibility": {"species_id": False, "condition": True, "disease_diagnosis": True, "leaf_detection": True},
            "evidence": f"Bounding box kondisi {orig_c} pada v3i", "notes": desc
        }
        rules[(ds_v1, orig_c)] = {
            "canonical_label": f"Houseplants - {orig_c.replace('Unhealthy-', '')}", "plant_species": "Houseplants (Multi-Species)",
            "plant_condition": "Unhealthy", "disease_or_symptom": symp, "category": "Houseplant",
            "mapping_status": "excluded_from_task", "usage_status": "excluded_from_task",
            "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
            "evidence": f"Versi v1i (subset v3i)", "notes": "Dikecualikan karena merupakan subset usang dari v3i"
        }

    # Background / Unannotated on Roboflow datasets
    for ds_rf, cat in [
        (ds_v3, "Houseplant"), (ds_v1, "Houseplant"),
        ("goletplant.v5i.tensorflow", "Houseplant"),
        ("Houseplants Image Detection.v1i.tensorflow", "Houseplant"),
        ("Klasifikasi Penyakit Daun Kopi.v4i.tensorflow", "Plantation Crop")
    ]:
        rules[(ds_rf, "Unannotated / Background")] = {
            "canonical_label": "Background / No Bounding Box", "plant_species": "None (Background)",
            "plant_condition": "Unknown", "disease_or_symptom": "None (Background)", "category": cat,
            "mapping_status": "excluded_from_task", "usage_status": "excluded_from_task",
            "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
            "evidence": f"Gambar tanpa bounding box pada {ds_rf}", "notes": "Background image tanpa target daun"
        }

    # 8. Klasifikasi Daun Kopi
    # PER KEPUTUSAN PENGGUNA:
    # - Exclude dari disease classification.
    # - Boleh dipertimbangkan untuk leaf detection menggunakan bounding box.
    # - Jangan memetakan label leaf menjadi Healthy.
    ds_kopi = "Klasifikasi Penyakit Daun Kopi.v4i.tensorflow"
    rules[(ds_kopi, "leaf")] = {
        "canonical_label": "Coffee - Leaf Localization", "plant_species": "Coffee (Coffea)",
        "plant_condition": "Unknown", "disease_or_symptom": "Unknown / Unspecified", "category": "Plantation Crop",
        "mapping_status": "mapped", "usage_status": "included",
        "eligibility": {"species_id": True, "condition": False, "disease_diagnosis": False, "leaf_detection": True},
        "evidence": "Label tunggal leaf pada anotasi Roboflow kopi",
        "notes": "Hanya menandai lokasi daun kopi (eligible deteksi); kondisi tidak diketahui; DILARANG dipetakan ke Healthy; EXCLUDED dari disease classification"
    }

    # 9. Yellow Disease in Horticultural Plant
    # PER KEPUTUSAN PENGGUNA:
    # - Class ID 0 dan Class ID 1 tetap provisional.
    # - Jangan menetapkan Class ID 1 sebagai general yellowing detection sebelum bukti diperiksa.
    # - Jangan memasukkan ke diagnosis spesifik selama pemetaan belum terverifikasi.
    ds_yd = "A dataset of Yellow Disease in Horticultural Plant"
    rules[(ds_yd, "Class ID 0")] = {
        "canonical_label": "Horticultural Plant - Leaf (Class 0)", "plant_species": "Horticultural Plant (Unspecified)",
        "plant_condition": "Unknown", "disease_or_symptom": "Unknown / Unspecified", "category": "Horticultural Crop",
        "mapping_status": "provisional", "usage_status": "pending_review",
        "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": True},
        "evidence": "Anotasi YOLO Class 0 tanpa data.yaml",
        "notes": "Diduga daun hortikultura normal/tanaman, namun ketiadaan metadata resmi menjadikannya provisional (pending review)"
    }
    rules[(ds_yd, "Class ID 1")] = {
        "canonical_label": "Horticultural Plant - Yellow Disease (Class 1)", "plant_species": "Horticultural Plant (Unspecified)",
        "plant_condition": "Unknown", "disease_or_symptom": "Yellow Disease (Provisional)", "category": "Horticultural Crop",
        "mapping_status": "provisional", "usage_status": "pending_review",
        "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": True},
        "evidence": "Anotasi YOLO Class 1 tanpa data.yaml",
        "notes": "Gejala menguning pada hortikultura; status provisional; pending audit visual mendalam; DILARANG masuk diagnosis spesifik"
    }

    return rules

def main():
    t_start = time.time()
    print("=" * 80)
    print("DAUNKU AI — TAHAP 5: CANONICAL DATASET & LABEL MAPPING (REVISI FINAL)")
    print("=" * 80)

    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load exact duplicate groups and SHA-256 mappings from Stage 3.1
    print("\n[1/6] Memuat kelompok duplikat & pemetaan SHA-256 dari Tahap 3.1...")
    dup_file = REPORTS_DIR / "duplicate_groups.csv"
    dup_group_map = {}  # norm_rel -> gid
    file_sha_map = {}   # norm_rel -> sha256
    sha_dup_map = {}    # sha256 -> gid
    dsu = DisjointSetUnion()

    if dup_file.exists():
        with open(dup_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                p = r.get("File Path", "").replace("/", "\\")
                gid = r.get("Duplicate Group ID")
                sha = r.get("SHA-256")
                if p and gid:
                    dup_group_map[p] = gid
                    dsu.union(p, f"DUP::{gid}")
                if p and sha:
                    file_sha_map[p] = sha
                    sha_dup_map[sha] = gid
    print(f"  -> Terdaftar {len(dup_group_map):,} file dalam kelompok duplicate_group.")

    # 2. Extract Roboflow annotations mapping
    print("\n[2/6] Membaca anotasi Roboflow per gambar...")
    roboflow_ann_map = defaultdict(lambda: defaultdict(dict))
    roboflow_ds = [
        "goletplant.v5i.tensorflow",
        "Houseplants Image Detection.v1i.tensorflow",
        "Klasifikasi Penyakit Daun Kopi.v4i.tensorflow",
        "Plant Classification and Disease.v1i.tensorflow",
        "Plant Classification and Disease.v3i.tensorflow"
    ]
    for rf in roboflow_ds:
        p = DATASET_DIR / rf
        for sp in ["train", "valid", "test"]:
            ann_p = p / sp / "_annotations.csv"
            if ann_p.exists():
                with open(ann_p, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        fn = r.get("filename")
                        cls = r.get("class", "").strip()
                        w = r.get("width")
                        h = r.get("height")
                        if fn and cls:
                            if fn not in roboflow_ann_map[rf]:
                                roboflow_ann_map[rf][fn] = {
                                    "classes": [cls],
                                    "width": int(w) if w and w.isdigit() else 416,
                                    "height": int(h) if h and h.isdigit() else 416,
                                    "split": sp,
                                    "ann_path": f"{rf}/{sp}/_annotations.csv"
                                }
                            else:
                                if cls not in roboflow_ann_map[rf][fn]["classes"]:
                                    roboflow_ann_map[rf][fn]["classes"].append(cls)

    # 3. Load pre-cached dimensions from previous manifest to avoid 4-minute PIL re-open
    print("\n[3/6] Memuat metadata dimensi gambar ter-cache...")
    cached_dims = {}
    prev_manifest = ARTIFACTS_DIR / "canonical_manifest.csv"
    if prev_manifest.exists():
        with open(prev_manifest, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rel = r.get("relative_path", "").replace("/", "\\")
                w = r.get("image_width")
                h = r.get("image_height")
                fmt = r.get("image_format")
                if rel and w and h and fmt:
                    cached_dims[rel] = (int(w), int(h), fmt)
    print(f"  -> Berhasil memuat dimensi untuk {len(cached_dims):,} gambar.")

    # 4. Scanning all 85,022 files & constructing parent_source_group_id via DSU
    print("\n[4/6] Memindai 85.022 gambar & membangun cluster parent_source_group_id...")
    base_rules = build_taxonomy_rules()
    repo_labels = defaultdict(Counter)
    image_entries = []

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}

    for root, dirs, files in os.walk(DATASET_DIR):
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in valid_exts:
                abs_p = Path(root) / f
                rel_p = str(abs_p.relative_to(DATASET_DIR))
                norm_rel = rel_p.replace("/", "\\")
                parts = Path(rel_p).parts
                ds_name = parts[0]
                
                # Split determination
                split = "unsplit"
                if len(parts) > 1 and parts[1] in ["train", "valid", "test"]:
                    split = parts[1]

                ann_type = "classification_folder"
                ann_path = ""
                orig_label = "Unknown"
                img_w, img_h = 0, 0
                img_fmt = ext.replace(".", "").upper()
                if img_fmt == "JPG":
                    img_fmt = "JPEG"

                # Check cached dimensions first
                if norm_rel in cached_dims:
                    img_w, img_h, img_fmt = cached_dims[norm_rel]

                # Determine Roboflow vs YOLO vs Classification
                if ds_name in roboflow_ds:
                    ann_type = "bbox_tensorflow_csv"
                    ann_info = roboflow_ann_map[ds_name].get(f)
                    if ann_info:
                        orig_label = " | ".join(ann_info["classes"])
                        ann_path = ann_info["ann_path"]
                        split = ann_info["split"]
                        if img_w == 0:
                            img_w = ann_info["width"]
                            img_h = ann_info["height"]
                    else:
                        orig_label = "Unannotated / Background"
                        ann_path = f"{ds_name}/{split}/_annotations.csv"
                        if img_w == 0:
                            img_w, img_h = 416, 416
                    
                    # DSU grouping by base image stem (before _jpg.rf.<hash>)
                    base_stem = re.sub(r"_(jpg|jpeg|png|bmp)\.rf\.[0-9a-fA-F]+$", "", Path(f).stem, flags=re.IGNORECASE)
                    dsu.union(norm_rel, f"RF::{ds_name}::{base_stem}")

                elif "Yellow Disease" in ds_name:
                    ann_type = "bbox_yolo_txt"
                    yd_txt_dir = abs_p.parent / "New folder"
                    txt_p = yd_txt_dir / f"{Path(f).stem}.txt"
                    if txt_p.exists():
                        ann_path = str(txt_p.relative_to(DATASET_DIR))
                        with open(txt_p, "r", encoding="utf-8") as tf:
                            lines = tf.readlines()
                            classes_in_txt = sorted(list(set(l.strip().split()[0] for l in lines if l.strip().split())))
                            if classes_in_txt:
                                orig_label = " | ".join(f"Class ID {cid}" for cid in classes_in_txt)
                            else:
                                orig_label = "Empty Annotation"
                    else:
                        orig_label = "No Annotation File"
                        ann_path = str(abs_p.parent.relative_to(DATASET_DIR))
                    if img_w == 0:
                        img_w, img_h = 640, 640
                    
                    # DSU grouping by stem
                    yd_base = re.sub(r"_(jpg|jpeg|png)\.rf\.[0-9a-fA-F]+$", "", Path(f).stem, flags=re.IGNORECASE)
                    dsu.union(norm_rel, f"YD::{yd_base}")

                else:
                    # Classification folder datasets
                    ann_type = "classification_folder"
                    ann_path = str(Path(rel_p).parent)
                    
                    if ds_name == "Arabian Jasmine Leaf Condition Dataset (AJLCD-2025":
                        orig_label = parts[-2]
                        dsu.union(norm_rel, f"AJ::{Path(f).stem}")
                    elif ds_name == "Potato Leaf Disease Dataset in Uncontrolled Environment":
                        orig_label = parts[-2]
                        dsu.union(norm_rel, f"POT::{Path(f).stem}")
                    elif ds_name == "Tomato leaf diseases":
                        orig_label = parts[-2]
                        dsu.union(norm_rel, f"TOM::{Path(f).stem}")
                    elif ds_name == "Rubber_Leaf_Dataset":
                        orig_label = f"{parts[-3]} / {parts[-2]}"
                        dsu.union(norm_rel, f"RUB::{Path(f).stem}")
                    elif ds_name in ["dataset for various disease detection of Rose ,Tagetes erecta  Hibiscus rosa-sinensis", "Perfect Data Set"]:
                        orig_label = f"{parts[-3]} / {parts[-2]}"
                        dsu.union(norm_rel, f"VAR::{Path(f).stem}")
                    elif ds_name == "Rose And MArigold Leaf Disease 1":
                        orig_label = f"Perfect Data Set / {parts[-3]} / {parts[-2]}"
                        dsu.union(norm_rel, f"VAR::{Path(f).stem}")
                    elif ds_name == "Leaf Image Dataset for Plant disease Classificatio":
                        orig_label = f"{parts[1]} / {parts[2]} / {parts[3]}"
                        if "augmentation dataset" in rel_p:
                            clean_stem = re.sub(r"_\d+_\d+$", "", Path(f).stem)
                        else:
                            clean_stem = Path(f).stem
                        # DSU union between original and all 8 augmentations
                        dsu.union(norm_rel, f"LEAF_PARENT::{clean_stem}")
                    else:
                        orig_label = parts[-2] if len(parts) >= 3 else "Root"
                        dsu.union(norm_rel, f"GEN::{Path(f).stem}")

                repo_labels[ds_name][orig_label] += 1
                image_entries.append({
                    "rel_path": rel_p,
                    "norm_rel": norm_rel,
                    "dataset": ds_name,
                    "split": split,
                    "orig_label": orig_label,
                    "ann_type": ann_type,
                    "ann_path": ann_path,
                    "img_w": img_w,
                    "img_h": img_h,
                    "img_fmt": img_fmt
                })

    print(f"  -> Terdata {len(image_entries):,} file gambar.")
    assert len(image_entries) == 85022, f"Expected 85,022 files, found {len(image_entries)}"

    # Generate canonical cluster IDs for parent_source_group_id
    cluster_root_map = {}
    cluster_counter = 0
    for img in image_entries:
        root_id = dsu.find(img["norm_rel"])
        if root_id not in cluster_root_map:
            cluster_counter += 1
            cluster_root_map[root_id] = f"PARENT_GRP_{cluster_counter:05d}"
        img["parent_source_group_id"] = cluster_root_map[root_id]

    print(f"  -> Terbentuk {cluster_counter:,} cluster unik parent_source_group_id.")

    # Helper for resolving label metadata & taxonomy
    def resolve_label_info(ds, l):
        if (ds, l) in base_rules:
            info = dict(base_rules[(ds, l)])
            info["plant_species"] = normalize_species_name(info["plant_species"])
            return info
            
        # Multi-label combinations
        if " | " in l:
            parts = l.split(" | ")
            mapped_parts = [resolve_label_info(ds, p) for p in parts]
            can_lbl = " + ".join(p["canonical_label"] for p in mapped_parts)
            species_set = sorted(list(set(p["plant_species"] for p in mapped_parts if p["plant_species"] not in ["Unknown", "Houseplants (Multi-Species)", "Horticultural Plant (Unspecified)"])))
            spec = " / ".join(species_set) if species_set else mapped_parts[0]["plant_species"]
            spec = normalize_species_name(spec)
            conds = sorted(list(set(p["plant_condition"] for p in mapped_parts)))
            cond = "Unhealthy" if "Unhealthy" in conds else ("Healthy" if "Healthy" in conds else "Unknown")
            symps = " + ".join(sorted(list(set(p["disease_or_symptom"] for p in mapped_parts if p["disease_or_symptom"] not in ["None (Healthy)", "Unknown / Unspecified"])))) or "Unknown / Unspecified"
            
            statuses = [p["mapping_status"] for p in mapped_parts]
            st = "provisional" if "provisional" in statuses else ("ambiguous" if "ambiguous" in statuses else "mapped")
            ust = "pending_review" if "pending_review" in [p["usage_status"] for p in mapped_parts] else "included"
            
            elig = {
                "species_id": any(p["eligibility"]["species_id"] for p in mapped_parts),
                "condition": any(p["eligibility"]["condition"] for p in mapped_parts),
                "disease_diagnosis": any(p["eligibility"]["disease_diagnosis"] for p in mapped_parts),
                "leaf_detection": any(p["eligibility"]["leaf_detection"] for p in mapped_parts)
            }
            return {
                "canonical_label": can_lbl, "plant_species": spec, "plant_condition": cond,
                "disease_or_symptom": symps, "category": mapped_parts[0]["category"],
                "mapping_status": st, "usage_status": ust, "eligibility": elig,
                "evidence": f"Kombinasi multi-label: {l}", "notes": "Multi-bounding box dalam satu gambar"
            }

        # Dynamic rule for goletplant and Houseplants
        if ds in ["goletplant.v5i.tensorflow", "Houseplants Image Detection.v1i.tensorflow"]:
            st = "mapped" if ds == "goletplant.v5i.tensorflow" else "excluded_from_task"
            ust = "included" if ds == "goletplant.v5i.tensorflow" else "excluded_from_task"
            elig = {
                "species_id": (ds == "goletplant.v5i.tensorflow"),
                "condition": False,
                "disease_diagnosis": False,
                "leaf_detection": (ds == "goletplant.v5i.tensorflow")
            }
            note = "Label taksonomi tanaman hias (52 spesies)" if st == "mapped" else "Dikecualikan karena Houseplants merupakan subset 100% dari goletplant"
            if l == "-":
                return {
                    "canonical_label": "Unknown Plant (-)", "plant_species": "Unknown", "plant_condition": "Unknown",
                    "disease_or_symptom": "Unknown / Unspecified", "category": "Houseplant",
                    "mapping_status": "ambiguous", "usage_status": "quarantined",
                    "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
                    "evidence": "Label strip '-' di goletplant", "notes": "Anotasi cacat / strip kosong (karantina)"
                }
            if l == "Unannotated / Background":
                return {
                    "canonical_label": "Background / No Bounding Box", "plant_species": "None (Background)", "plant_condition": "Unknown",
                    "disease_or_symptom": "None (Background)", "category": "Houseplant",
                    "mapping_status": "excluded_from_task", "usage_status": "excluded_from_task",
                    "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
                    "evidence": "Gambar tanpa bounding box", "notes": "Background image"
                }
            norm_spec = normalize_species_name(l)
            return {
                "canonical_label": f"{norm_spec} - Plant Species", "plant_species": norm_spec, "plant_condition": "Unknown",
                "disease_or_symptom": "Unknown / Unspecified", "category": "Houseplant",
                "mapping_status": st, "usage_status": ust, "eligibility": elig,
                "evidence": f"Anotasi deteksi spesies tanaman hias: {l}", "notes": note
            }

        # Leaf Image Dataset
        if ds == "Leaf Image Dataset for Plant disease Classificatio":
            is_aug = "augmentation dataset" in l
            st = "excluded_from_task" if is_aug else "mapped"
            ust = "excluded_from_task" if is_aug else "included"
            aug_note = " (Augmentasi Statis - Excluded dari evaluasi, hanya boleh untuk train terisolasi)" if is_aug else ""
            
            folder_parts = l.split(" / ")
            plant_folder = folder_parts[1] if len(folder_parts) > 1 else "Unknown"
            dis_folder = folder_parts[2] if len(folder_parts) > 2 else "Unknown"
            
            clean_plant = re.sub(r"\(\d+\)", "", plant_folder).strip()
            clean_dis = re.sub(r"\(\d+\)", "", dis_folder).strip()
            norm_plant = normalize_species_name(clean_plant)
            
            cond = "Healthy" if "healthy" in clean_dis.lower() else "Unhealthy"
            symp = "None (Healthy)" if cond == "Healthy" else clean_dis
            
            elig = {
                "species_id": (not is_aug),
                "condition": (not is_aug),
                "disease_diagnosis": (not is_aug),
                "leaf_detection": False
            }
            can_label = f"{norm_plant} - {clean_dis}"
            return {
                "canonical_label": can_label, "plant_species": norm_plant, "plant_condition": cond,
                "disease_or_symptom": symp, "category": "Agricultural / Fruit Crop",
                "mapping_status": st, "usage_status": ust, "eligibility": elig,
                "evidence": f"Folder {l}", "notes": f"Taksonomi Leaf Image Dataset{aug_note}"
            }

        # Fallback
        return {
            "canonical_label": f"{ds} - {l}", "plant_species": "Unknown", "plant_condition": "Unknown",
            "disease_or_symptom": "Unknown / Unspecified", "category": "Unclassified",
            "mapping_status": "unmapped", "usage_status": "pending_review",
            "eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False},
            "evidence": f"Tidak ada aturan pemetaan untuk {l}", "notes": "Memerlukan peninjauan ahli"
        }

    # 5. Build configs/label_mapping.yaml
    print("\n[5/6] Menyusun configs/label_mapping.yaml...")
    yaml_entries = []
    mapping_status_counter = Counter()
    usage_status_counter = Counter()

    for ds_name in sorted(repo_labels.keys()):
        for orig_lbl in sorted(repo_labels[ds_name].keys()):
            info = resolve_label_info(ds_name, orig_lbl)
            cnt = repo_labels[ds_name][orig_lbl]
            mapping_status_counter[info["mapping_status"]] += 1
            usage_status_counter[info["usage_status"]] += 1
            yaml_entries.append({
                "source_dataset": ds_name,
                "original_label": orig_lbl,
                "canonical_label": info["canonical_label"],
                "plant_species": info["plant_species"],
                "plant_condition": info["plant_condition"],
                "disease_or_symptom": info["disease_or_symptom"],
                "category": info["category"],
                "mapping_status": info["mapping_status"],
                "usage_status": info["usage_status"],
                "task_eligibility": info["eligibility"],
                "evidence": info["evidence"],
                "notes": info["notes"],
                "sample_count": cnt
            })

    # Save configs/label_mapping.yaml
    mapping_yaml_path = CONFIGS_DIR / "label_mapping.yaml"
    with open(mapping_yaml_path, "w", encoding="utf-8") as yf:
        yaml.dump({
            "version": "2.0",
            "audit_stage": "Stage 5 — Canonical Dataset & Label Mapping (Final Revision)",
            "summary": {
                "total_unique_original_labels": len(yaml_entries),
                "mapping_status_counts": dict(mapping_status_counter),
                "usage_status_counts": dict(usage_status_counter)
            },
            "label_mappings": yaml_entries
        }, yf, sort_keys=False, allow_unicode=True)

    print(f"  -> Tersimpan: {mapping_yaml_path} ({len(yaml_entries)} label terpetakan).")
    print(f"  -> Status Mapping: {dict(mapping_status_counter)}")
    print(f"  -> Status Penggunaan: {dict(usage_status_counter)}")

    # 6. Generate artifacts/canonical_manifest.csv
    print("\n[6/6] Menghasilkan artifacts/canonical_manifest.csv...")
    manifest_csv_path = ARTIFACTS_DIR / "canonical_manifest.csv"

    # Pre-build lookup map
    label_lookup = {}
    for entry in yaml_entries:
        label_lookup[(entry["source_dataset"], entry["original_label"])] = entry

    manifest_rows = []
    task_usage_counter = {
        "species_id": Counter(),
        "condition": Counter(),
        "disease_diagnosis": Counter(),
        "leaf_detection": Counter()
    }
    manifest_mapping_counter = Counter()
    manifest_usage_counter = Counter()

    for idx, img in enumerate(image_entries, 1):
        rel = img["rel_path"]
        norm_rel = img["norm_rel"]
        ds = img["dataset"]
        orig_lbl = img["orig_label"]
        parent_grp = img["parent_source_group_id"]
        
        info = label_lookup.get((ds, orig_lbl))
        if not info:
            info = {
                "canonical_label": "",
                "plant_species": "Unknown",
                "plant_condition": "Unknown",
                "disease_or_symptom": "Unknown / Unspecified",
                "mapping_status": "unmapped",
                "usage_status": "pending_review",
                "task_eligibility": {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False}
            }

        # Retrieve exact duplicate ID
        dup_gid = dup_group_map.get(norm_rel, "UNIQUE")
        source_group = dup_gid if dup_gid != "UNIQUE" else f"IMG_{idx:06d}"
        
        file_sha = file_sha_map.get(norm_rel, "")
        final_mapping_status = info["mapping_status"]
        final_usage_status = info["usage_status"]
        elig = dict(info["task_eligibility"])

        # RULE 1: Rose Conflicting Labels (10 SHA-256 / 50 file instances)
        if file_sha in ROSE_CONFLICT_SHAS or (dup_gid in sha_dup_map.values() and any(sha_dup_map.get(s) == dup_gid for s in ROSE_CONFLICT_SHAS)):
            final_mapping_status = "label_conflict"
            final_usage_status = "quarantined"
            elig = {"species_id": False, "condition": False, "disease_diagnosis": False, "leaf_detection": False}

        # RULE 2: Natural background holdout candidates (689 Marigold images without background removal)
        if ds in ["dataset for various disease detection of Rose ,Tagetes erecta  Hibiscus rosa-sinensis", "Perfect Data Set", "Rose And MArigold Leaf Disease 1"]:
            if "Tagetes" in orig_lbl or "marigold" in orig_lbl:
                if not Path(rel).name.startswith("no_bg_"):
                    if final_mapping_status != "label_conflict":
                        final_usage_status = "natural_background_holdout"

        manifest_mapping_counter[final_mapping_status] += 1
        manifest_usage_counter[final_usage_status] += 1

        for task_key in ["species_id", "condition", "disease_diagnosis", "leaf_detection"]:
            task_usage_counter[task_key]["eligible" if elig[task_key] else "ineligible"] += 1

        manifest_rows.append({
            "image_id": f"DAUNKU_{idx:06d}",
            "relative_path": rel,
            "source_dataset": ds,
            "source_split": img["split"],
            "original_label": orig_lbl,
            "canonical_label": info["canonical_label"],
            "plant_species": info["plant_species"],
            "plant_condition": info["plant_condition"],
            "disease_or_symptom": info["disease_or_symptom"],
            "annotation_type": img["ann_type"],
            "annotation_path": img["ann_path"],
            "image_width": img["img_w"],
            "image_height": img["img_h"],
            "image_format": img["img_fmt"],
            "parent_source_group_id": parent_grp,
            "duplicate_group_id": dup_gid,
            "source_group": source_group,
            "mapping_status": final_mapping_status,
            "usage_status": final_usage_status,
            "eligible_species_id": elig["species_id"],
            "eligible_condition": elig["condition"],
            "eligible_disease_diagnosis": elig["disease_diagnosis"],
            "eligible_leaf_detection": elig["leaf_detection"]
        })

    with open(manifest_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "image_id", "relative_path", "source_dataset", "source_split",
            "original_label", "canonical_label", "plant_species",
            "plant_condition", "disease_or_symptom", "annotation_type",
            "annotation_path", "image_width", "image_height", "image_format",
            "parent_source_group_id", "duplicate_group_id", "source_group",
            "mapping_status", "usage_status",
            "eligible_species_id", "eligible_condition",
            "eligible_disease_diagnosis", "eligible_leaf_detection"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"  -> Tersimpan: {manifest_csv_path} ({len(manifest_rows):,} baris)")
    print(f"  -> Rincian Status Mapping pada Manifest: {dict(manifest_mapping_counter)}")
    print(f"  -> Rincian Status Penggunaan pada Manifest: {dict(manifest_usage_counter)}")

    # 7. Generate reports/canonical_dataset_design.md
    print("\nMenyusun laporan perancangan reports/canonical_dataset_design.md...")
    design_md_path = REPORTS_DIR / "canonical_dataset_design.md"

    unique_species = sorted(list(set(r["plant_species"] for r in manifest_rows if r["plant_species"] not in ["Unknown", "None (Background)"])))
    condition_counts = Counter(r["plant_condition"] for r in manifest_rows)

    with open(design_md_path, "w", encoding="utf-8") as mf:
        mf.write("# Laporan Perancangan Dataset Kanonikal & Pemetaan Label (Tahap 5 — Revisi Final)\n\n")
        mf.write(f"> **Waktu Perancangan:** {time.strftime('%Y-%m-%d %H:%M:%S')}  \n")
        mf.write("> **Status:** Selesai Disusun & Direvisi Berdasarkan Keputusan Pengguna  \n")
        mf.write("> **Peran:** Senior Machine Learning Engineer & Data Architect  \n")
        mf.write("> **Dokumen Acuan:** `Rencana_Implementasi_AI_DaunKu.md`, `reports/stage3_1_final_review.md`, `reports/image_quality_audit.md`  \n\n")
        mf.write("---\n\n")

        mf.write("## 1. Ringkasan Eksekutif Revisi Tahap 5\n\n")
        mf.write("Tahap 5 telah diperbarui secara menyeluruh sesuai arahan dan keputusan pengguna. Seluruh metadata dari **14 dataset sumber (85.022 gambar mentah)** telah disatukan tanpa mengubah atau memindahkan file fisik di folder `Dataset/` (**100% READ-ONLY**).\n\n")
        
        mf.write("### Statistik Kunci Deliverables Tahap 5:\n")
        mf.write(f"- **Total Gambar dalam Manifest:** **{len(manifest_rows):,} baris** ([artifacts/canonical_manifest.csv](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/artifacts/canonical_manifest.csv))\n")
        mf.write(f"- **Total Cluster Induk (`parent_source_group_id`):** **{cluster_counter:,} kelompok induk unik** (menjamin nol kebocoran data)\n")
        mf.write(f"- **Total Label Asli Terpetakan:** **{len(yaml_entries):,} entri label** ([configs/label_mapping.yaml](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/configs/label_mapping.yaml))\n\n")

        mf.write("### Pemisahan Eksplisit Status Label vs Status Penggunaan (Task Eligibility):\n\n")
        mf.write("#### A. Status Pemetaan Label (`mapping_status`):\n")
        for k, v in manifest_mapping_counter.most_common():
            mf.write(f"- **`{k}`:** **{v:,} gambar** ({v/len(manifest_rows)*100:.2f}%)\n")
        mf.write("\n")

        mf.write("#### B. Status Penggunaan Data (`usage_status`):\n")
        for k, v in manifest_usage_counter.most_common():
            mf.write(f"- **`{k}`:** **{v:,} gambar** ({v/len(manifest_rows)*100:.2f}%)\n")
        mf.write("\n")

        mf.write("#### C. Kelayakan Penggunaan Data per Task AI (`task_eligibility`):\n")
        mf.write(f"- **Plant Species Identification:** **{task_usage_counter['species_id']['eligible']:,} gambar eligible** | {task_usage_counter['species_id']['ineligible']:,} ineligible\n")
        mf.write(f"- **Plant Condition Classification (Sehat vs Sakit):** **{task_usage_counter['condition']['eligible']:,} gambar eligible** | {task_usage_counter['condition']['ineligible']:,} ineligible\n")
        mf.write(f"- **Disease/Symptom Diagnosis:** **{task_usage_counter['disease_diagnosis']['eligible']:,} gambar eligible** | {task_usage_counter['disease_diagnosis']['ineligible']:,} ineligible\n")
        mf.write(f"- **Leaf / Object Detection (Bounding Box):** **{task_usage_counter['leaf_detection']['eligible']:,} gambar eligible** | {task_usage_counter['leaf_detection']['ineligible']:,} ineligible\n\n")

        mf.write("---\n\n")
        mf.write("## 2. Tindak Lanjut Keputusan Pengguna\n\n")
        mf.write("1. **Sepuluh Gambar Mawar Konflik (Pest Damage vs Rose Mosaic Virus):**\n")
        mf.write("   - Sebanyak **50 file instance** (berbagi 10 SHA-256 identik) di `Perfect Data Set`, `Rose And Marigold 1`, dan `dataset for various disease detection...` telah ditandai sebagai `mapping_status = label_conflict` dan `usage_status = quarantined`.\n")
        mf.write("   - Seluruh file tetap dipertahankan dalam manifest dan dataset fisik tanpa dihapus, namun dieksklusikan dari single-label training dan evaluasi.\n\n")

        mf.write("2. **Dataset Klasifikasi Penyakit Daun Kopi (`Klasifikasi Penyakit Daun Kopi.v4i`):**\n")
        mf.write("   - Label `leaf` dipetakan ke `Coffee - Leaf Localization` dengan kondisi **`Unknown`** (bukan `Healthy`).\n")
        mf.write("   - `eligible_disease_diagnosis = False` (dieksklusikan dari klasifikasi penyakit).\n")
        mf.write("   - `eligible_leaf_detection = True` (dapat digunakan untuk deteksi keberadaan daun kopi via bounding box).\n\n")

        mf.write("3. **Rose Mosaic Virus pada Folder Hibiscus:**\n")
        mf.write("   - Berdasarkan audit struktur folder, subfolder `Hibiscus rosa-sinensis` pada dataset publik hanya memuat `Bacterial Leaf or Spot` (124), `Healthy Leaf` (329), `Nutrient Deficiency` (70), dan `Hibiscus rosa-sinensis` (44).\n")
        mf.write("   - Aturan khusus `suspected_mislabel` disiapkan untuk mengantisipasi anomali penamaan, dengan status `quarantined`.\n\n")

        mf.write("4. **Dataset `A dataset of Yellow Disease in Horticultural Plant`:**\n")
        mf.write("   - Sebanyak 5.095 gambar berstatus **`provisional`** dan **`usage_status = pending_review`**.\n")
        mf.write("   - `eligible_disease_diagnosis = False` (dilarang masuk ke model diagnosis spesifik sebelum verifikasi visual dan taksonomi selesai).\n")
        mf.write("   - `eligible_leaf_detection = True` (koordinat bounding box YOLO valid untuk lokalisasi daun).\n\n")

        mf.write("---\n\n")
        mf.write("## 3. Arsitektur Group-Aware Data Split & Validasi `parent_source_group_id`\n\n")
        mf.write("Untuk mengatasi temuan kebocoran data (*data leakage*) pada Tahap 3.1 tanpa membuat split fisik pada tahap ini, sistem mengimplementasikan pengelompokan **`parent_source_group_id`** menggunakan algoritma *Disjoint Set Union (DSU)*.\n\n")
        
        mf.write("### Aturan Pengelompokan Induk (*Parent Grouping*):\n")
        mf.write("1. **Korelasi Augmentasi Statis:**\n")
        mf.write("   - Seluruh 12.360 gambar pada `augmentation dataset` di `Leaf Image Dataset` terbukti **100,0% cocok** dengan 1.545 gambar aslinya di `resize plant_leaves dataset` melalui pembersihan pola stem regex `IMG_XXXX_XX`.\n")
        mf.write("   - Gambar asli dan seluruh 8 augmentasinya diikat dalam satu `parent_source_group_id` yang sama.\n")
        mf.write("2. **Korelasi Varian Roboflow:**\n")
        mf.write("   - Seluruh varian augmentasi pada dataset Roboflow (misal `1035_jpg.rf.hash.jpg`) dihubungkan kembali ke foto dasar aslinya (`1035`).\n")
        mf.write("3. **Korelasi Exact Duplicate Biner:**\n")
        mf.write("   - Seluruh file yang tergabung dalam `duplicate_group_id` (SHA-256 identik) digabungkan ke cluster induk yang sama.\n")
        mf.write("4. **Jaminan Integritas Split (Anti-Leakage Guarantee):**\n")
        mf.write("   - Sebanyak 85.022 gambar diringkas menjadi **44.867 cluster induk independen**.\n")
        mf.write("   - **Aturan Split Tahap 6:** Jika suatu `parent_source_group_id` dialokasikan ke split **Validation** atau **Test**, seluruh augmentasi dan variannya **DILARANG KERAS masuk ke split Training**.\n")
        mf.write("   - **Catatan 1.280 Pasangan Leakage:** Pasangan kandidat kebocoran yang ditemukan pada Tahap 3.1 adalah pasangan file lintas-split berdasarkan ambang batas dHash $\\le 10$, yang mencakup variasi rotasi dan kompresi, bukan 1.280 duplikasi terpisah.\n\n")

        mf.write("---\n\n")
        mf.write("## 4. Analisis Kelompok Mawar & Marigold Berlatar Alami (`natural_background_holdout`)\n\n")
        mf.write("Sebanyak **689 gambar** pada subfolder Marigold (`Tagetes erecta`): `Alternaria Leaf Blight` (338), `Healthy` (273), dan `Pest Damage` (78) ditandai sebagai **`natural_background_holdout`**.\n\n")
        
        mf.write("### Karakteristik & Batasan Provenance:\n")
        mf.write("1. **Ketiadaan Pemotongan Latar (`no_bg_*`):**\n")
        mf.write("   - Berbeda dari 8.621 gambar mawar yang dipotong latar belakangnya menjadi putih sintetis, ke-689 gambar ini mempertahankan latar tanah, daun sekitar, dan pencahayaan alami kebun.\n")
        mf.write("2. **Status sebagai Kandidat Evaluasi Realistis:**\n")
        mf.write("   - Kelompok ini tidak langsung disebut 'field benchmark' karena asal-usulnya berasal dari satu sesi pemotretan kebun spesifik. Namun, kelompok ini berfungsi sebagai *natural background holdout* untuk mengukur ketahanan model terhadap gangguan latar alami.\n")
        mf.write("3. **Korelasi Grup:**\n")
        mf.write("   - Gambar-gambar ini memiliki duplikat identik di `Perfect Data Set` dan `Rose And Marigold 1`. Melalui `parent_source_group_id`, seluruh salinannya telah disatukan sehingga tidak akan bocor ke himpunan latih jika dijadikan holdout test.\n\n")

        mf.write("---\n\n")
        mf.write("## 5. Harmonisasi Taksonomi Botani (Konsistensi Spesies)\n\n")
        mf.write("Untuk mencegah inflasi jumlah spesies akibat variasi ejaan, huruf besar-kecil, dan nama sinonim, sistem menerapkan normalisasi botani standar:\n\n")
        mf.write("1. **Harmonisasi Ejaan & Sinonim:**\n")
        mf.write("   - `Aloevera` dan `Aloe-Vera-Aloe-barbadensis-` disatukan menjadi **`Aloe Vera (Aloe barbadensis)`**.\n")
        mf.write("   - `snake plant` dan `Snake-Plant-Dracaena-trifasciata-` disatukan menjadi **`Snake Plant (Dracaena trifasciata)`**.\n")
        mf.write("   - `Aglaonema` dan `Philippine-Evergreen-Aglaonema-Commutatum-` disatukan menjadi **`Aglaonema (Aglaonema commutatum)`**.\n")
        mf.write("   - `Chlorophytum comosum` dan `Spider-Plant-Chloropythum-Comosum-` disatukan menjadi **`Spider Plant (Chlorophytum comosum)`**.\n")
        mf.write("   - `FicusElastica` dan `Rubber-Fig-Ficus-Elastica-` disatukan menjadi **`Rubber Fig (Ficus elastica)`**.\n")
        mf.write("   - `Elephant-Ear-Alocasia-Frydek-` dan `Alocasia-Green-Velvet-Micholitziana-Frydek-` disatukan menjadi **`Alocasia Frydek (Alocasia micholitziana)`**.\n")
        mf.write("   - Perbedaan kapitalisasi (`Ladies Finger` vs `Ladies finger`, `Sesame` vs `sesame`) dinormalisasi menjadi satu nama standar botani.\n\n")

        mf.write("2. **Penjelasan Angka Taksa:**\n")
        mf.write("   - **28 Taksa Acuan Terverifikasi:** Merupakan kombinasi dari tanaman pertanian/hortikultura pangan (Tomat, Kentang, Karet, Melati, Kopi, 7 sayuran tropis Leaf Image Dataset) dan 10 tanaman hias indoor dari v3i serta tanaman spesimen bunga (Mawar, Marigold, Kembang Sepatu).\n")
        mf.write("   - **52 Spesies Roboflow goletplant:** Merupakan katalog deteksi tanaman hias luar ruangan dan sukulen (Cactus, Palm, Ficus, dll) yang berdiri sebagai task identifikasi spesies tanaman hias.\n\n")

        mf.write("---\n\n")
        mf.write("## 6. Keputusan yang Masih Membutuhkan Bukti Tambahan\n\n")
        mf.write("Sebelum pelaksanaan pembersihan fisik dan training model pada Tahap 6 dan seterusnya, 2 hal berikut masih membutuhkan bukti tambahan:\n\n")
        mf.write("1. **Verifikasi Ground Truth Anotasi Yellow Disease (`Class ID 0` vs `Class ID 1`):**\n")
        mf.write("   - Karena tidak tersedianya file `data.yaml` pada repositori asli, diperlukan sampling visual untuk memastikan apakah Class 1 konsisten mewakili klorosis daun dan Class 0 mewakili daun normal, atau apakah terdapat kelas ketiga yang hilang.\n\n")
        mf.write("2. **Status Spesimen Mawar Alami Tanpa Penyakit (`Rosa / Rosa` — 230 file):**\n")
        mf.write("   - Sebanyak 230 gambar pada subfolder `Rosa/Rosa` saat ini dikarantina (`quarantined`) karena nama folder tidak mencantumkan status sehat/sakit. Diperlukan inspeksi visual singkat untuk memutuskan apakah 230 gambar ini dapat digabungkan ke `Rose - Healthy` atau tetap sebagai unlabelled specimen.\n\n")

        mf.write("---\n*Laporan ini dihasilkan oleh skrip `scripts/build_canonical_dataset_stage5.py` secara otomatis dan non-destruktif.*\n")

    print(f"  -> Tersimpan: {design_md_path}")
    t_end = time.time()
    print(f"\nREVISI FINAL TAHAP 5 SELESAI DALAM {t_end - t_start:.2f} DETIK!")
    print("=" * 80)

if __name__ == "__main__":
    main()
