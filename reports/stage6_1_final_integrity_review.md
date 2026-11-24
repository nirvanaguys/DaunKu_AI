# Laporan Audit Integritas Akhir: Stage 6.1 Final Split Review DaunKu AI

> **Waktu Audit:** 2026-11-24 11:07:17  
> **Status Audit:** **VALID, RECONCILED, & INTEGRITY VERIFIED (100% Kepatuhan)**  
> **Peran:** Senior Machine Learning Engineer, Dataset Auditor, & Data Architect  
> **Dokumen yang Diperiksa:**  
> - `artifacts/splits/split_manifest.csv`  
> - `artifacts/splits/train_manifest.csv`, `validation_manifest.csv`, `test_manifest.csv`  
> - `artifacts/splits/natural_background_holdout.csv`  
> - `artifacts/splits/split_config.yaml` & `split_summary.json`  
> - `reports/audit_879_leakage_decisions.csv` & `reports/data_split_plan.md`  

---

## 1. Ringkasan Eksekutif Hasil Review Tahap 6.1

Audit final independen (Tahap 6.1) telah selesai dilaksanakan secara **read-only** tanpa memodifikasi dataset asli, aplikasi Flutter, taksonomi Stage 5, maupun manifest split Stage 6.

### Hasil Utama Audit Integritas:
1. **Manifest Reconciliation (85.022 Baris):**  
   Seluruh **85.022 baris data** pada `split_manifest.csv` terbukti unik (**0 missing, 0 duplicate, 0 unaccounted rows**). Setiap baris memiliki alokasi split eksplisit pada seluruh 4 task AI.
2. **Eligibility Reconciliation:**  
   Perbedaan antara jumlah gambar eligible Stage 5 dan jumlah gambar aktif (Train+Val+Test) Stage 6 **100% berhasil direkonsiliasi dan dibuktikan secara matematis**. Selisih tersebut murni berasal dari isolasi data `holdout` (689 foto Marigold alami) dan data `quarantined` (726 melati tahap awal, 230 mawar tanpa keterangan, dll). Tidak ada data eligible yang hilang tanpa alasan.
3. **Leakage Reconciliation (1.280 Pasangan):**  
   - Seluruh **1.280 pasangan potential leakage terbukti 100% konsisten berada pada `meta_component_id` yang sama**.
   - **Tingkat Kebocoran Data (Data Leakage):** **0 pasangan (0,00%)** melintasi split Train, Validation, dan Test pada seluruh 4 task AI.
   - **Rekonsiliasi 138 vs 136 Pasangan dHash $\le 1$:** Terbukti secara biner bahwa 2 pasangan dist=0 telah terserap di dalam 401 pasangan DSU awal, menyisakan tepat 136 pasangan pada 879 pasangan unmerged ($138 - 2 = 136$).
4. **Meta-Component & Augmentation Integrity:**  
   - **0 parent group yang terpecah** ke meta-component berbeda.
   - **12.360 augmentasi Leaf Image Dataset 100,0% berada pada meta-component yang sama** dengan 1.545 foto aslinya.
   - **0 augmentasi yang bocor ke Train** saat foto aslinya berada di Validation atau Test.
5. **Evaluation Coverage & Rare Classes:**  
   Sebanyak 30 kelas langka pada Species ID, 3 kelas pada Disease Diagnosis, dan 50 kelas pada Leaf Detection (seluruhnya kombinasi multi-bounding box langka) dialokasikan secara konservatif ke Train Set, dan telah didokumentasikan sebagai batasan evaluasi model.
6. **Reproducibility:**  
   Prosedur pembagian terbukti deterministik menggunakan `seed = 42` dan metode `group_aware_stratified_meta_component`.

---

## 2. Pemeriksaan A: Rekonsiliasi Manifest 85.022 Baris

Seluruh 85.022 baris pada `artifacts/splits/split_manifest.csv` memiliki status alokasi yang lengkap dan saling eksklusif:

| Status Alokasi / Split | Species ID | Plant Condition | Disease Diagnosis | Leaf Detection |
| :--- | ---: | ---: | ---: | ---: |
| **`train`** (Himpunan Pelatihan) | 37.500 | 13.109 | 13.107 | 27.600 |
| **`validation`** (Himpunan Validasi) | 6.068 | 2.799 | 2.788 | 4.888 |
| **`test`** (Himpunan Uji Terkunci / Locked Test) | 6.062 | 2.841 | 2.854 | 4.582 |
| **`holdout`** (Kandidat Evaluasi Alami) | 2.067 | 2.067 | 2.067 | 2.067 |
| **`quarantined`** (Data Karantina / Konflik) | 1.266 | 1.266 | 1.266 | 1.266 |
| **`not_in_task`** (Tidak Memenuhi Syarat Task) | 32.059 | 62.940 | 62.940 | 44.619 |
| **TOTAL VERIFIKASI** | **85.022** | **85.022** | **85.022** | **85.022** |

### Verifikasi Baris:
- **Baris Hilang (*Missing Rows*):** **0 baris**
- **Baris Ganda (*Duplicate Rows*):** **0 baris**
- **Baris Tanpa Alokasi (*Unaccounted Rows*):** **0 baris**
- **Path Relatif Unik:** Tepat **85.022 path unik**.

---

## 3. Pemeriksaan B: Rekonsiliasi Eligibility Stage 5 vs Stage 6

Terdapat perbedaan angka antara gambar eligible pada Stage 5 (`canonical_manifest.csv`) dengan gambar aktif (Train + Val + Test) pada Stage 6 (`split_manifest.csv`). Seluruh perbedaan berhasil direkonsiliasi dengan rincian berikut:

| Task Pemodelan AI | Stage 5 Eligible | Stage 6 Aktif (Train+Val+Test) | Selisih Baris | Penyebab & Rincian File Selisih |
| :--- | :---: | :---: | :---: | :--- |
| **1. Plant Species Identification** | **51.532** | **49.630** | **-1.902** | • **689 gambar** dialokasikan ke `holdout` (Marigold alami).<br>• **1.213 gambar** dialokasikan ke `quarantined` (726 melati Initial stage, 230 Rosa/Rosa, 213 Tagetes/Tagetes, 44 Hibiscus/Hibiscus).<br>*(689 + 1.213 = 1.902)* |
| **2. Plant Condition Classification** | **20.164** | **18.749** | **-1.415** | • **689 gambar** dialokasikan ke `holdout` (Marigold alami).<br>• **726 gambar** dialokasikan ke `quarantined` (Melati Initial stage, kondisi Unhealthy namun dikarantina dari evaluasi utama).<br>*(689 + 726 = 1.415)* |
| **3. Disease/Symptom Diagnosis** | **19.438** | **18.749** | **-689** | • **Tepat 689 gambar** dialokasikan ke `holdout` (Marigold berlatar alami). Pada Stage 5 berstatus eligible, namun pada Stage 6 diisolasi penuh ke `natural_background_holdout`.<br>*(Selisih = 689)* |
| **4. Leaf/Object Detection** | **37.070** | **37.070** | **0** | **Cocok Sempurna (100,00%).** Seluruh 37.070 gambar eligible masuk ke Train (27.600), Val (4.888), dan Test (4.582). |

> [!NOTE]
> Selisih di atas membuktikan bahwa perancangan Stage 6 sangat disiplin: data berstatus `holdout` (evaluasi latar alami) dan data `quarantined` (ambigu/konflik) **dikeluarkan dari split training aktif** agar tidak mencemari model.

---

## 4. Pemeriksaan C: Rekonsiliasi 1.280 Pasangan *Potential Data Leakage*

Audit terhadap 1.280 pasangan potential leakage dari Stage 3.1:

### 1. Struktur 1.280 Pasangan:
- **401 Pasangan Terhubung di DSU Awal Stage 5:**
  - 100 pasangan exact duplicate biner lintas-split.
  - 299 pasangan turunan Roboflow dari foto dasar yang sama (`_jpg.rf.hash`).
  - 2 pasangan dHash = 0.
- **879 Pasangan Diaudit di Stage 6:**
  - 136 pasangan `likely_same_source` (48 pasangan dHash=0, 88 pasangan dHash=1).
  - 222 pasangan `uncertain` (dHash=2).
  - 521 pasangan `visually_similar_not_duplicate` (dHash=3).

### 2. Rekonsiliasi Selisih 138 vs 136 Pasangan dHash $\le 1$:
- Pada seluruh 1.280 pasangan di Stage 3.1: terdapat 50 pasangan dist=0 (non-exact) + 88 pasangan dist=1 = **138 pasangan**.
- Dari 50 pasangan dist=0 tersebut, **2 pasangan telah diserap ke dalam 401 pasangan DSU awal**.
- Sehingga pada 879 pasangan yang belum terserap DSU, tersisa 48 pasangan dist=0 + 88 pasangan dist=1 = **136 pasangan**.
- **Terbukti secara biner:** $138 - 2 = 136$ pasangan.

### 3. Pemeriksaan Konsistensi Endpoint (Zero Leakage Check):
Pemeriksaan dilakukan terhadap setiap endpoint (File 1 dan File 2) dari seluruh 1.280 pasangan pada seluruh task AI:
- **Pasangan dengan meta_component berbeda:** **0 pasangan (0,00%)**
- **Pasangan yang terpecah lintas-split pada Species ID:** **0 pasangan (0,00%)** ✅
- **Pasangan yang terpecah lintas-split pada Condition:** **0 pasangan (0,00%)** ✅
- **Pasangan yang terpecah lintas-split pada Disease Diagnosis:** **0 pasangan (0,00%)** ✅
- **Pasangan yang terpecah lintas-split pada Leaf Detection:** **0 pasangan (0,00%)** ✅

---

## 5. Pemeriksaan D: Integritas Meta-Component & Augmentasi

1. **Konsistensi Parent ke Meta-Component:**
   - Total parent groups: **31.997**.
   - Total meta-components: **31.604**.
   - Parent group yang memiliki lebih dari satu meta-component: **0 (0,00%)** ✅.
2. **Integritas Augmentasi Leaf Image Dataset:**
   - Foto asli (`resize`): **1.545 foto**.
   - Foto augmentasi (`augmentation`): **12.360 foto**.
   - Augmentasi dengan meta-component mismatch terhadap foto aslinya: **0 foto (0,00%)** ✅.
   - Augmentasi yang masuk ke Train sementara foto aslinya di Validation/Test: **0 foto (0,00%)** ✅.

---

## 6. Pemeriksaan E: Cakupan Evaluasi & Analisis Kelas Langka (*Rare Classes*)

Strategi group-aware mengelompokkan data berdasarkan unit foto dasar independen. Untuk kelas dengan jumlah grup $\le 2$, stratifikasi biasa tidak dapat membagi data ke Train, Val, dan Test tanpa memecah grup:

| Task Pemodelan AI | Total Kelas | Kelas Langka (<3 Grup) | Alokasi Split | Keterbatasan Evaluasi Model |
| :--- | :---: | :---: | :---: | :--- |
| **Plant Species Identification** | 103 kelas | **30 kelas** | Train (atau 1 Train, 1 Test jika n=2) | Kelas multi-spesies Roboflow langka (misal *Alocasia + Golden Pothos*) tidak memiliki sampel validasi independen. Evaluasi harus difokuskan pada 52 spesies tunggal utama. |
| **Plant Condition Classification** | 2 kelas | **0 kelas** | Terbagi Seimbang (70 / 15 / 15) | Tidak ada kelas langka. Seluruh kelas (Healthy & Unhealthy) terwakili seimbang di Train, Val, dan Test. |
| **Disease/Symptom Diagnosis** | 53 kelas | **3 kelas** | Train | 3 kelas multi-gejala langka v3i (*Overwatering + Rust*, dll) dialokasikan ke Train. 50 kelas penyakit tunggal terwakili penuh di seluruh split. |
| **Leaf/Object Detection** | 149 kelas | **50 kelas** | Train (atau 1 Train, 1 Test) | Kombinasi multi-label bounding box langka hanya dievaluasi pada deteksi objek murni (per-box IoU). |

---

## 7. Pemeriksaan F: Reproducibility & Integritas Konfigurasi

- **Random Seed:** **`42`** (tercatat di `split_config.yaml`, `split_manifest.csv`, dan skrip eksekusi).
- **Metode Pembagian:** **`group_aware_stratified_meta_component`**.
- **Deterministik Penuh:** Pengurutan simetris stabil (`key = lambda x: x[0]`) diterapkan sebelum pengacakan seed, menjamin hasil split akan selalu identik 100% pada setiap eksekusi ulang.
- **Verifikasi Locked Test Set:** Himpunan uji disimpan di `artifacts/splits/test_manifest.csv` dan terisolasi secara permanen dari proses pelatihan maupun tuning model.

---

## 8. Git Status Pemeriksaan Akhir

```text
Untracked files:
  artifacts/splits/
  reports/audit_879_leakage_decisions.csv
  reports/data_split_plan.md
  reports/stage6_1_final_integrity_review.md
  reports/stage6_1_integrity_issues.csv
  scripts/audit_879_leakage_pairs.py
  scripts/audit_stage6_1_integrity.py
  scripts/generate_stage6_1_reports.py
  scripts/generate_stage6_splits.py
  scripts/phase1_audit_splits.py
  scripts/phase3_task_split_planner.py
```
- Folder `Dataset/` dan `daunku_app/` **100% bersih dan tidak tersentuh**.
- Tidak ada modifikasi pada `canonical_manifest.csv` maupun `label_mapping.yaml`.
- Tidak ada commit atau push yang dilakukan.

---

**STATUS: AUDIT TAHAP 6.1 SELESAI & STOP.**  
*Seluruh kriteria penutupan Tahap 6.1 telah terpenuhi secara sempurna. Eksekusi dihentikan. Saya menunggu keputusan dan persetujuan resmi Anda sebelum melangkah ke Tahap 7 (Training / Baseline Model).*
