# Laporan Perencanaan & Strategi Pembagian Data (Tahap 6 — Data Splitting & Leakage Control)

> **Waktu Penyusunan:** 2026-11-24 10:50:12  
> **Status:** Selesai Disusun & Tervalidasi Otomatis (Zero Leakage Verified)  
> **Peran:** Senior Machine Learning Engineer, Dataset Auditor, & Data Architect  
> **Artefak Dihasilkan:** `artifacts/splits/split_manifest.csv`, `train_manifest.csv`, `validation_manifest.csv`, `test_manifest.csv`, `natural_background_holdout.csv`, `split_config.yaml`, `split_summary.json`  

---

## 1. Ringkasan Eksekutif Tahap 6

Tahap 6 bertujuan merancang dan mengeksekusi strategi pembagian data (*data splitting*) yang **group-aware**, bebas dari kebocoran data (*zero leakage*), dan dapat direproduksi secara deterministik (*seed=42*) untuk mendukung 4 task pemodelan AI DaunKu. Seluruh 85.022 gambar mentah pada folder `Dataset/` tetap **100% READ-ONLY**.

### Statistik Kunci Pemisahan Data:
- **Total Gambar Dimanifestasikan:** **85.022 gambar** ([artifacts/splits/split_manifest.csv](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/artifacts/splits/split_manifest.csv))
- **Total Parent Groups Dasar:** **31,997 kelompok induk**
- **Total Meta-Components Bebas Bocor:** **31,604 komponen terisolasi**
- **Constraint Pasangan Near-Duplicate Diterapkan:** **879 batasan pairwise** (mengunci kedua endpoint 879 pasangan leakage ke split yang sama)
- **Kebocoran Data Lintas-Split:** **0 pasangan (0,00%)** pada seluruh task AI
- **Kebocoran Augmentasi ke Latih:** **0 gambar (0,00%)** (seluruh augmentasi mengikuti alokasi foto asli)

---

## 2. Audit Split Bawaan (*Built-in Splits Audit*)

Sebelum pembagian baru dibuat, inventarisasi menyeluruh dilakukan terhadap struktur folder bawaan dari 14 dataset sumber:

| No | Nama Dataset Sumber | Existing Train | Existing Validation | Existing Test | Split Quality | Rekomendasi Auditor |
| :-: | :--- | ---: | ---: | ---: | :---: | :--- |
| 1 | `goletplant.v5i.tensorflow` | 25.373 | 22 | 668 | `not_reliable` | **Tolak Split Bawaan**. Validasi hanya 22 gambar untuk 52 kelas spesies (sangat tidak seimbang). Gunakan split baru berbasis group. |
| 2 | `Houseplants Image Detection.v1i` | 5.967 | 4 | 84 | `not_reliable` | **Tolak Split Bawaan**. Validasi hanya 4 gambar untuk 1 kelas; 100% subset redundan dari goletplant. Status: `excluded_from_task`. |
| 3 | `Klasifikasi Daun Kopi.v4i` | 2.804 | 263 | 149 | `not_reliable` | **Tolak Split Bawaan**. Terbukti 102 parent groups bocor melintasi train/valid/test bawaan. Gunakan split baru berbasis group. |
| 4 | `Plant Classification and Disease.v1i` | 563 | 46 | 19 | `not_reliable` | **Tolak Split Bawaan**. Versi usang/subset dari v3i. Status: `excluded_from_task`. |
| 5 | `Plant Classification and Disease.v3i` | 2.921 | 178 | 85 | `usable_with_restrictions` | Terdapat 11 parent groups bocor pada split bawaan. Perlu restrukturisasi group-aware. |
| 6 | `Tomato leaf diseases` | 0 | 0 | 0 | `no_existing_split` | Tidak memiliki split bawaan (2.627 gambar folder klasifikasi). Wajib dibuatkan split kanonikal. |
| 7 | `Potato Leaf Disease Dataset` | 0 | 0 | 0 | `no_existing_split` | Tidak memiliki split bawaan (3.076 gambar folder klasifikasi). Wajib dibuatkan split kanonikal. |
| 8 | `Arabian Jasmine (AJLCD-2025)` | 0 | 0 | 0 | `no_existing_split` | Tidak memiliki split bawaan (6.315 gambar folder klasifikasi). Wajib dibuatkan split kanonikal. |
| 9 | `Rubber_Leaf_Dataset` | 0 | 0 | 0 | `no_existing_split` | Format Raw vs Compressed (3.481 gambar). Wajib dibuatkan split kanonikal dari Raw saja. |
| 10 | `dataset for various disease detection...` | 0 | 0 | 0 | `no_existing_split` | Tidak memiliki split bawaan (4.479 gambar). Wajib dibuatkan split kanonikal. |
| 11 | `Perfect Data Set` | 0 | 0 | 0 | `no_existing_split` | Redundan dengan dataset No. 10. Status: `excluded_from_task`. |
| 12 | `Rose And MArigold Leaf Disease 1` | 0 | 0 | 0 | `no_existing_split` | Duplikat persis Perfect Data Set. Status: `excluded_from_task`. |
| 13 | `Leaf Image Dataset (Original & Aug)` | 0 | 0 | 0 | `no_existing_split` | Format resize vs augmentasi (13.905 gambar). Wajib dibuatkan split berbasis parent foto asli. |
| 14 | `Yellow Disease in Horticultural Plant` | 0 | 0 | 0 | `no_existing_split` | Format folder deteksi (5.095 gambar). Status: `pending_review` untuk diagnosis, eligible untuk lokalisasi. |

### Kesimpulan Audit Split Bawaan:
- **Split Bawaan Roboflow Tidak Layak Dipertahankan:** Rasio validasi yang sangat kerdil (hanya 4–22 gambar) dan kebocoran 102 parent group pada Daun Kopi serta 11 parent group pada v3i membuktikan bahwa evaluasi model di atas split bawaan akan menghasilkan akurasi bias (*data leakage over-optimism*).
- **Sebagian Besar Dataset Tidak Memiliki Split:** 9 dari 14 dataset sumber sama sekali tidak memiliki split bawaan sehingga memerlukan perancangan split kanonikal terpadu.

---

## 3. Hasil Pemeriksaan 879 Pasangan *Potential Data Leakage*

Audit khusus dilakukan terhadap 879 pasangan potential leakage lintas-split yang belum terserap DSU dasar Stage 5:

### Rincian Keputusan Audit 879 Pasangan:
- **`visually_similar_not_duplicate` (521 pasangan / 59,27%):** Pasangan dengan $dHash = 3$ dan nama file dasar berbeda. Merupakan gambar daun tanaman sejenis dengan orientasi atau latar belakang yang memiliki kemiripan perseptual, bukan duplikat dari foto sumber yang sama.
- **`uncertain` (222 pasangan / 25,26%):** Pasangan dengan $dHash = 2$ pada nama file berbeda. Berpotensi sebagai foto berturutan (*burst mode*) atau daun berbeda pada tanaman yang sama.
- **`likely_same_source` (136 pasangan / 15,47%):** Pasangan dengan $dHash = 0$ (48 pasangan) dan $dHash = 1$ (88 pasangan). Memiliki kemiripan visual sangat tinggi akibat kompresi JPEG berulang atau variasi crop minor.

### Penanganan Konservatif melalui *Connected Components*:
Sesuai aturan ketat proyek, sistem **tidak membuang pasangan tanpa bukti**, melainkan memperlakukan seluruh 879 pasangan sebagai **constraint konservatif provisi**.
1. Dibangun graf relasi di mana simpul adalah `parent_source_group_id` dan sisi adalah pasangan leakage.
2. Terbentuk **56 connected components** yang mencakup 449 parent groups.
3. **Penggabungan Meta-Components:** Seluruh parent groups dalam satu component disatukan menjadi satu `meta_component_id` tunggal (**31.604 meta-components**).
4. **Jaminan Nol Kebocoran:** Alokasi split (Train, Val, Test) dilakukan pada level `meta_component_id`. Dengan demikian, **kedua sisi dari seluruh 879 pasangan dipastikan 100% berada pada split yang sama**, mengeliminasi risiko kebocoran data secara tuntas.

---

## 4. Strategi & Distribusi Pembagian per Task AI

Pembagian data dilakukan secara independen untuk setiap task AI dengan mematuhi kelayakan label (`task_eligibility`) dari manifest kanonikal Stage 5:

### A. Task: Plant Species Identification (`species_id`)

- **Rasio Target:** Train 75.0% | Validation 12.5% | Test 12.5%
- **Distribusi Gambar:**
  - **Train:** **37,500 gambar** (75.56%)
  - **Validation:** **6,068 gambar** (12.23%)
  - **Test (Locked Test Set):** **6,062 gambar** (12.21%)
- **Data Terisolasi:** Holdout = **2,067** | Quarantined = **1,266** | Not in Task = **32,059**
- **Kelas Langka (<3 groups):** **30 kelas** (seluruhnya dialokasikan ke Train untuk mencegah validation/test set hampa tanpa memecah group)

### A. Task: Plant Condition Classification (`condition`)

- **Rasio Target:** Train 70.0% | Validation 15.0% | Test 15.0%
- **Distribusi Gambar:**
  - **Train:** **13,109 gambar** (69.92%)
  - **Validation:** **2,799 gambar** (14.93%)
  - **Test (Locked Test Set):** **2,841 gambar** (15.15%)
- **Data Terisolasi:** Holdout = **2,067** | Quarantined = **1,266** | Not in Task = **62,940**
- **Kelas Langka (<3 groups):** **0 kelas** (seluruhnya dialokasikan ke Train untuk mencegah validation/test set hampa tanpa memecah group)

### A. Task: Disease/Symptom Diagnosis (`disease_diagnosis`)

- **Rasio Target:** Train 70.0% | Validation 15.0% | Test 15.0%
- **Distribusi Gambar:**
  - **Train:** **13,107 gambar** (69.91%)
  - **Validation:** **2,788 gambar** (14.87%)
  - **Test (Locked Test Set):** **2,854 gambar** (15.22%)
- **Data Terisolasi:** Holdout = **2,067** | Quarantined = **1,266** | Not in Task = **62,940**
- **Kelas Langka (<3 groups):** **3 kelas** (seluruhnya dialokasikan ke Train untuk mencegah validation/test set hampa tanpa memecah group)

### A. Task: Leaf/Object Detection (Bounding Box) (`leaf_detection`)

- **Rasio Target:** Train 75.0% | Validation 12.5% | Test 12.5%
- **Distribusi Gambar:**
  - **Train:** **27,600 gambar** (74.45%)
  - **Validation:** **4,888 gambar** (13.19%)
  - **Test (Locked Test Set):** **4,582 gambar** (12.36%)
- **Data Terisolasi:** Holdout = **2,067** | Quarantined = **1,266** | Not in Task = **44,619**
- **Kelas Langka (<3 groups):** **50 kelas** (seluruhnya dialokasikan ke Train untuk mencegah validation/test set hampa tanpa memecah group)

---

## 5. Himpunan Evaluasi Terisolasi & Locked Test Set

### 1. Kandidat Evaluasi Alami (`natural_background_holdout` — 2.067 File Instance):
- Berasal dari 689 foto Marigold berlatar alami kebun tanpa pemotongan latar belakang (`no_bg_*`).
- Disimpan secara terpisah dalam `artifacts/splits/natural_background_holdout.csv`.
- **Kebijakan Evaluasi:** Berfungsi sebagai *external-style holdout benchmark* untuk menguji ketahanan model terhadap gangguan latar tanah, rumput, dan variasi cahaya kebun sesungguhnya. **DILARANG dicampur ke dalam data training.**

### 2. Kebijakan Locked Test Set:
- Himpunan Test pada masing-masing task disimpan dalam `artifacts/splits/test_manifest.csv`.
- **Protokol Integritas:** Locked Test Set **hanya boleh disentuh satu kali pada akhir proyek** untuk pelaporan metrik performa akhir. Dilarang keras digunakan untuk tuning hyperparameter, pemilihan arsitektur model, atau pemilihan threshold deteksi.

---

## 6. Instruksi Reproducibility & Validasi Otomatis

1. **Deterministik Penuh:** Pembagian data dikontrol oleh `SPLIT_SEED = 42` menggunakan pengurutan simetris stabil sebelum pengacakan.
2. **Skrip Reproduksi:** Seluruh manifest dapat dibangun ulang secara deterministik dan non-destruktif menggunakan perintah:
   ```bash
   python scripts/generate_stage6_splits.py
   ```
3. **Hasil Pemeriksaan Otomatis:**
   - Tepat 85.022 path relatif unik (0 missing, 0 duplicate rows) ✅
   - 0 parent group yang terpecah lintas-split pada seluruh task ✅
   - 0 meta-component yang terpecah lintas-split pada seluruh task ✅
   - 0 exact duplicate biner lintas-split pada seluruh task ✅
   - 0 augmentasi Leaf Image yang bocor ke training saat foto aslinya di val/test ✅
   - 0 gambar berstatus quarantined/pending_review masuk ke task terlarang ✅
   - 0 gambar holdout yang tercampur ke dalam training ✅

---
*Laporan ini dihasilkan oleh skrip `scripts/generate_stage6_splits.py` secara otomatis dan non-destruktif.*
