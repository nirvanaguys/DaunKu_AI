# DaunKu AI — Komponen Kecerdasan Buatan Aplikasi DaunKu

Repositori ini memuat dokumentasi audit dataset, manifest kanonis, pembagian data bebas kebocoran (*group-aware split*), rancangan arsitektur model, serta rencana eksperimen untuk komponen **Artificial Intelligence (AI)** pada aplikasi **DaunKu**.

DaunKu adalah aplikasi mobile untuk membantu pengguna merawat tanaman melalui identifikasi tanaman berbasis foto, indikasi kondisi/gejala daun, rekomendasi perawatan berbasis basis pengetahuan (*knowledge base*), dan layanan pendamping berkebun.

---

## 📁 Struktur Repositori (`main`)

```text
daunku_ai/
├── artifacts/                # Inventaris JSON, canonical_manifest.csv, dan split Stage 6
├── configs/                  # Pemetaan label kanonis (label_mapping.yaml)
├── reports/                  # Laporan audit Stage 0–6.1 & dokumen arsitektur Stage 7
├── scripts/                  # Skrip Python mandiri untuk audit, pemetaan, dan splitting
├── .gitignore                # Pengecualian dataset mentah, virtualenv, dan checkpoint
├── DaunKu_Analisis_Dataset_dan_Rancangan_AI.md  # Dokumen analisis awal dataset
├── Rencana_Implementasi_AI_DaunKu.md           # Pedoman dan roadmap implementasi bertahap
└── README.md                 # Dokumentasi repositori
```

> **Catatan Pengelolaan Data & Branch:**
> - Dataset mentah (~19,2 GB / 85.022 gambar) dikelola secara lokal pada direktori `Dataset/` dalam kondisi **read-only** dan dikecualikan dari pelacakan Git melalui `.gitignore`.
> - Branch **`main`** menyimpan seluruh fondasi data & arsitektur **Stage 0–7 (`COMPLETE`)**.
> - Eksperimen **Stage 8.1 (Pilot Training Task 1 di Google Colab GPU)** dikerjakan secara terpisah pada branch **`stage8-task1-pilot`** agar tidak mencemari branch `main`.

---

## 📊 Ringkasan Koleksi Dataset (Status Audit Aktual)

Berdasarkan audit rekursif dan validasi biner menggunakan Pillow, seluruh **85.022 gambar** dari **14 folder dataset** berada dalam kondisi valid (**0 file rusak / zero corruption**):

| No | Nama Dataset | Tipe Tugas | Format Anotasi | Total Gambar | Cakupan / Komoditas |
| :-: | :--- | :--- | :--- | :---: | :--- |
| **1** | `goletplant.v5i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 26.063 | 52 varietas tanaman hias populer |
| **2** | `Leaf Image Dataset for Plant disease Classificatio` | Klasifikasi | Folder per Kelas | 13.905 | 7 tanaman sayuran pekarangan & penyakit |
| **3** | `Arabian Jasmine Leaf Condition Dataset (AJLCD-2025` | Klasifikasi | Folder per Kelas | 6.315 | Bunga Melati (*kondisi kesehatan*) |
| **4** | `Houseplants Image Detection.v1i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 6.055 | 24 tanaman hias (*subset murni goletplant*) |
| **5** | `A dataset of Yellow Disease in Horticultural Plant` | Deteksi Objek | YOLO Darknet (`.txt`) | 5.095 | Penyakit kuning hortikultura (*provisional*) |
| **6** | `dataset for various disease detection of Rose,Tagetes,Hibiscus` | Klasifikasi | Folder per Kelas | 4.479 | Mawar, Marigold, dan Kembang Sepatu |
| **7** | `Rubber_Leaf_Dataset` | Klasifikasi | Folder per Kelas | 3.481 | Daun Karet (*4 kondisi penyakit*) |
| **8** | `Perfect Data Set` | Klasifikasi | Folder per Kelas | 3.449 | Daun Mawar & Marigold (*subset induk No. 6*) |
| **9** | `Rose And MArigold Leaf Disease 1` | Klasifikasi | Folder per Kelas | 3.449 | *Duplikat persis 100% dari No. 8* |
| **10** | `Klasifikasi Penyakit Daun Kopi.v4i.tensorflow` | Deteksi Objek | TF CSV | 3.216 | Daun Kopi (*anotasi 'leaf'*) |
| **11** | `Plant Classification and Disease.v3i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 3.184 | 10 tanaman hias + 7 gejala perawatan daun |
| **12** | `Potato Leaf Disease Dataset in Uncontrolled Environment` | Klasifikasi | Folder per Kelas | 3.076 | Daun Kentang (*7 kelas patogen*) |
| **13** | `Tomato leaf diseases` | Klasifikasi | Folder per Kelas | 2.627 | Daun Tomat (*10 kelas penyakit*) |
| **14** | `Plant Classification and Disease.v1i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 628 | *Subset murni dari v3i* |
| | **TOTAL KESELURUHAN (Mentah)** | | | **85.022** | **Kapasitas Disk: ~19,2 GB** |

---

## 🎯 Ringkasan Split & Baseline 4 Task AI (Stage 6 & Stage 7)

Seluruh pembagian data dilakukan secara **group-aware berdasarkan `meta_component_id`** (`SPLIT_SEED = 42`) dengan isolasi penuh terhadap *natural-background holdout* (2.067 baris / 689 foto dasar Marigold) dan data *quarantined* (1.266 baris):

| Task AI | Train / Val / Locked Test (Aktif) | Cakupan Kelas Baseline | Kandidat Model (Rekomendasi) |
| :--- | :---: | :--- | :--- |
| **1. Plant Species Identification** | 37.408 / 6.068 / 6.047 *(49.523)* | **68 kelas single-species** *(37 kombinasi = 107 img dipisahkan)* | `EfficientNet-B0`, `MobileNetV3-Large` |
| **2. Plant Condition Classification** | 13.109 / 2.799 / 2.841 *(18.749)* | **2 kelas** (`Healthy` 18,51% vs `Unhealthy` 81,49%) | `MobileNetV3-Small`, `EfficientNet-B0` |
| **3. Disease/Symptom Diagnosis** | 13.107 / 2.788 / 2.854 *(18.749)* | **53 kelas aktif** (50 di semua split, 3 train-only) | `EfficientNet-B0`, `ResNet50` |
| **4. Object / Leaf Detection** | 23.791 / 4.251 / 3.933 *(31.975 — 4A)* | **70 kelas atomik terverifikasi** *(+ 2 `Yellow Disease` provisional dipisahkan)* | `YOLOv8n`, `YOLO11n` |

> **Catatan:** Seluruh model, FastAPI, ONNX/TFLite, Knowledge Base, dan integrasi Flutter (`daunku_app`) saat ini masih berstatus **rancangan (*planned/conceptual*)** dan belum diimplementasikan.

---

## 🚀 Status Roadmap Pengembangan AI

Mengacu pada dokumen kerja [Rencana_Implementasi_AI_DaunKu.md](./Rencana_Implementasi_AI_DaunKu.md):

* [x] **Tahap 0 — Pemeriksaan Lingkungan:** Verifikasi Windows 11, Python 3.13.9, RAM 16 GB (CPU only), dan strategi training GPU di Google Colab (`reports/environment_audit.md`).
* [x] **Tahap 1 — Inventarisasi Dataset:** Audit 14 dataset, 85.022 file gambar, dan struktur split sumber (`reports/dataset_inventory.md`).
* [x] **Tahap 2 — Audit Label & Anotasi:** Audit kelas dan 944 catatan kualitas anotasi (`reports/label_and_annotation_audit.md`).
* [x] **Tahap 3 & 3.1 — Audit Duplikasi & Kebocoran Data:** Deteksi SHA-256 exact duplicate, perceptual near-duplicate (dHash), validasi visual, dan 1.280 pasangan potential leakage (`reports/duplicate_audit.md`, `reports/stage3_1_final_review.md`).
* [x] **Tahap 4 — Pemeriksaan Kualitas Visual:** Audit resolusi, class imbalance, dan bias latar belakang (`reports/image_quality_audit.md`).
* [x] **Tahap 5 — Pemetaan Label & Manifest Kanonis:** Standarisasi 85.022 baris (`artifacts/canonical_manifest.csv`, `configs/label_mapping.yaml`, `reports/stage5_final_validation.md`).
* [x] **Tahap 6 & 6.1 — Group-Aware Data Splitting & Final Integrity Review:** Pembagian deterministik berbasis `meta_component_id` (`seed = 42`, *zero known/audited leakage pairs across splits* intra-task, Locked Test & Holdout terisolasi; `artifacts/splits/`, `reports/stage6_1_final_integrity_review.md`).
* [x] **Tahap 7 — Rekomendasi Arsitektur & Rencana Eksperimen Baseline (`STAGE 7 COMPLETE`):** Rancangan arsitektur modular, protokol `inner_val` / `val_cal` / `val_thresh` / `E_test`, diagram pipeline konseptual, dan review konsistensi final (`reports/model_architecture_recommendation.md`, `reports/baseline_experiment_plan.md`, `reports/model_pipeline_diagram.md`, `reports/stage7_final_consistency_review.md`).
* [ ] **Tahap 8 — Eksperimen Training (In Progress di branch `stage8-task1-pilot`):** Pilot training Task 1 (`EfficientNet-B0`, maks. 3 epoch di Google Colab GPU) sebelum full training.
* [ ] **Tahap 9–12 — Evaluasi Model Final, Basis Pengetahuan Perawatan, Pipeline Inferensi, & API FastAPI.**
* [ ] **Tahap 13–14 — Integrasi Aplikasi Flutter (`daunku_app`) & Dokumentasi Serah Terima.**

---

## 🛠️ Skrip Audit Utama

Untuk mereproduksi audit integritas dataset atau split secara lokal (read-only terhadap `Dataset/`):

```bash
python scripts/run_audit_stage0_to_2.py
python scripts/audit_stage6_1_integrity.py
```
