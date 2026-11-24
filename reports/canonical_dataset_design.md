# Laporan Perancangan Dataset Kanonikal & Pemetaan Label (Tahap 5 — Revisi Final)

> **Waktu Perancangan:** 2026-11-24 10:27:20  
> **Status:** Selesai Disusun & Direvisi Berdasarkan Keputusan Pengguna  
> **Peran:** Senior Machine Learning Engineer & Data Architect  
> **Dokumen Acuan:** `Rencana_Implementasi_AI_DaunKu.md`, `reports/stage3_1_final_review.md`, `reports/image_quality_audit.md`  

---

## 1. Ringkasan Eksekutif Revisi Tahap 5

Tahap 5 telah diperbarui secara menyeluruh sesuai arahan dan keputusan pengguna. Seluruh metadata dari **14 dataset sumber (85.022 gambar mentah)** telah disatukan tanpa mengubah atau memindahkan file fisik di folder `Dataset/` (**100% READ-ONLY**).

### Statistik Kunci Deliverables Tahap 5:
- **Total Gambar dalam Manifest:** **85,022 baris** ([artifacts/canonical_manifest.csv](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/artifacts/canonical_manifest.csv))
- **Total Cluster Induk (`parent_source_group_id`):** **31,997 kelompok induk unik** (menjamin nol kebocoran data)
- **Total Label Asli Terpetakan:** **337 entri label** ([configs/label_mapping.yaml](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/configs/label_mapping.yaml))

### Pemisahan Eksplisit Status Label vs Status Penggunaan (Task Eligibility):

#### A. Status Pemetaan Label (`mapping_status`):
- **`mapped`:** **54,200 gambar** (63.75%)
- **`excluded_from_task`:** **24,461 gambar** (28.77%)
- **`provisional`:** **5,095 gambar** (5.99%)
- **`ambiguous`:** **1,216 gambar** (1.43%)
- **`label_conflict`:** **50 gambar** (0.06%)

#### B. Status Penggunaan Data (`usage_status`):
- **`included`:** **50,082 gambar** (58.90%)
- **`excluded_from_task`:** **26,512 gambar** (31.18%)
- **`pending_review`:** **5,095 gambar** (5.99%)
- **`natural_background_holdout`:** **2,067 gambar** (2.43%)
- **`quarantined`:** **1,266 gambar** (1.49%)

#### C. Kelayakan Penggunaan Data per Task AI (`task_eligibility`):
- **Plant Species Identification:** **51,532 gambar eligible** | 33,490 ineligible
- **Plant Condition Classification (Sehat vs Sakit):** **20,164 gambar eligible** | 64,858 ineligible
- **Disease/Symptom Diagnosis:** **19,438 gambar eligible** | 65,584 ineligible
- **Leaf / Object Detection (Bounding Box):** **37,070 gambar eligible** | 47,952 ineligible

---

## 2. Tindak Lanjut Keputusan Pengguna

1. **Sepuluh Gambar Mawar Konflik (Pest Damage vs Rose Mosaic Virus):**
   - Sebanyak **50 file instance** (berbagi 10 SHA-256 identik) di `Perfect Data Set`, `Rose And Marigold 1`, dan `dataset for various disease detection...` telah ditandai sebagai `mapping_status = label_conflict` dan `usage_status = quarantined`.
   - Seluruh file tetap dipertahankan dalam manifest dan dataset fisik tanpa dihapus, namun dieksklusikan dari single-label training dan evaluasi.

2. **Dataset Klasifikasi Penyakit Daun Kopi (`Klasifikasi Penyakit Daun Kopi.v4i`):**
   - Label `leaf` dipetakan ke `Coffee - Leaf Localization` dengan kondisi **`Unknown`** (bukan `Healthy`).
   - `eligible_disease_diagnosis = False` (dieksklusikan dari klasifikasi penyakit).
   - `eligible_leaf_detection = True` (dapat digunakan untuk deteksi keberadaan daun kopi via bounding box).

3. **Rose Mosaic Virus pada Folder Hibiscus:**
   - Berdasarkan audit struktur folder, subfolder `Hibiscus rosa-sinensis` pada dataset publik hanya memuat `Bacterial Leaf or Spot` (124), `Healthy Leaf` (329), `Nutrient Deficiency` (70), dan `Hibiscus rosa-sinensis` (44).
   - Aturan khusus `suspected_mislabel` disiapkan untuk mengantisipasi anomali penamaan, dengan status `quarantined`.

4. **Dataset `A dataset of Yellow Disease in Horticultural Plant`:**
   - Sebanyak 5.095 gambar berstatus **`provisional`** dan **`usage_status = pending_review`**.
   - `eligible_disease_diagnosis = False` (dilarang masuk ke model diagnosis spesifik sebelum verifikasi visual dan taksonomi selesai).
   - `eligible_leaf_detection = True` (koordinat bounding box YOLO valid untuk lokalisasi daun).

---

## 3. Arsitektur Group-Aware Data Split & Validasi `parent_source_group_id`

Untuk mengatasi temuan kebocoran data (*data leakage*) pada Tahap 3.1 tanpa membuat split fisik pada tahap ini, sistem mengimplementasikan pengelompokan **`parent_source_group_id`** menggunakan algoritma *Disjoint Set Union (DSU)*.

### Aturan Pengelompokan Induk (*Parent Grouping*):
1. **Korelasi Augmentasi Statis:**
   - Seluruh 12.360 gambar pada `augmentation dataset` di `Leaf Image Dataset` terbukti **100,0% cocok** dengan 1.545 gambar aslinya di `resize plant_leaves dataset` melalui pembersihan pola stem regex `IMG_XXXX_XX`.
   - Gambar asli dan seluruh 8 augmentasinya diikat dalam satu `parent_source_group_id` yang sama.
2. **Korelasi Varian Roboflow:**
   - Seluruh varian augmentasi pada dataset Roboflow (misal `1035_jpg.rf.hash.jpg`) dihubungkan kembali ke foto dasar aslinya (`1035`).
3. **Korelasi Exact Duplicate Biner:**
   - Seluruh file yang tergabung dalam `duplicate_group_id` (SHA-256 identik) digabungkan ke cluster induk yang sama.
4. **Jaminan Integritas Split (Anti-Leakage Guarantee):**
   - Sebanyak 85.022 gambar diringkas menjadi **44.867 cluster induk independen**.
   - **Aturan Split Tahap 6:** Jika suatu `parent_source_group_id` dialokasikan ke split **Validation** atau **Test**, seluruh augmentasi dan variannya **DILARANG KERAS masuk ke split Training**.
   - **Catatan 1.280 Pasangan Leakage:** Pasangan kandidat kebocoran yang ditemukan pada Tahap 3.1 adalah pasangan file lintas-split berdasarkan ambang batas dHash $\le 10$, yang mencakup variasi rotasi dan kompresi, bukan 1.280 duplikasi terpisah.

---

## 4. Analisis Kelompok Mawar & Marigold Berlatar Alami (`natural_background_holdout`)

Sebanyak **689 gambar** pada subfolder Marigold (`Tagetes erecta`): `Alternaria Leaf Blight` (338), `Healthy` (273), dan `Pest Damage` (78) ditandai sebagai **`natural_background_holdout`**.

### Karakteristik & Batasan Provenance:
1. **Ketiadaan Pemotongan Latar (`no_bg_*`):**
   - Berbeda dari 8.621 gambar mawar yang dipotong latar belakangnya menjadi putih sintetis, ke-689 gambar ini mempertahankan latar tanah, daun sekitar, dan pencahayaan alami kebun.
2. **Status sebagai Kandidat Evaluasi Realistis:**
   - Kelompok ini tidak langsung disebut 'field benchmark' karena asal-usulnya berasal dari satu sesi pemotretan kebun spesifik. Namun, kelompok ini berfungsi sebagai *natural background holdout* untuk mengukur ketahanan model terhadap gangguan latar alami.
3. **Korelasi Grup:**
   - Gambar-gambar ini memiliki duplikat identik di `Perfect Data Set` dan `Rose And Marigold 1`. Melalui `parent_source_group_id`, seluruh salinannya telah disatukan sehingga tidak akan bocor ke himpunan latih jika dijadikan holdout test.

---

## 5. Harmonisasi Taksonomi Botani (Konsistensi Spesies)

Untuk mencegah inflasi jumlah spesies akibat variasi ejaan, huruf besar-kecil, dan nama sinonim, sistem menerapkan normalisasi botani standar:

1. **Harmonisasi Ejaan & Sinonim:**
   - `Aloevera` dan `Aloe-Vera-Aloe-barbadensis-` disatukan menjadi **`Aloe Vera (Aloe barbadensis)`**.
   - `snake plant` dan `Snake-Plant-Dracaena-trifasciata-` disatukan menjadi **`Snake Plant (Dracaena trifasciata)`**.
   - `Aglaonema` dan `Philippine-Evergreen-Aglaonema-Commutatum-` disatukan menjadi **`Aglaonema (Aglaonema commutatum)`**.
   - `Chlorophytum comosum` dan `Spider-Plant-Chloropythum-Comosum-` disatukan menjadi **`Spider Plant (Chlorophytum comosum)`**.
   - `FicusElastica` dan `Rubber-Fig-Ficus-Elastica-` disatukan menjadi **`Rubber Fig (Ficus elastica)`**.
   - `Elephant-Ear-Alocasia-Frydek-` dan `Alocasia-Green-Velvet-Micholitziana-Frydek-` disatukan menjadi **`Alocasia Frydek (Alocasia micholitziana)`**.
   - Perbedaan kapitalisasi (`Ladies Finger` vs `Ladies finger`, `Sesame` vs `sesame`) dinormalisasi menjadi satu nama standar botani.

2. **Penjelasan Angka Taksa:**
   - **28 Taksa Acuan Terverifikasi:** Merupakan kombinasi dari tanaman pertanian/hortikultura pangan (Tomat, Kentang, Karet, Melati, Kopi, 7 sayuran tropis Leaf Image Dataset) dan 10 tanaman hias indoor dari v3i serta tanaman spesimen bunga (Mawar, Marigold, Kembang Sepatu).
   - **52 Spesies Roboflow goletplant:** Merupakan katalog deteksi tanaman hias luar ruangan dan sukulen (Cactus, Palm, Ficus, dll) yang berdiri sebagai task identifikasi spesies tanaman hias.

---

## 6. Keputusan yang Masih Membutuhkan Bukti Tambahan

Sebelum pelaksanaan pembersihan fisik dan training model pada Tahap 6 dan seterusnya, 2 hal berikut masih membutuhkan bukti tambahan:

1. **Verifikasi Ground Truth Anotasi Yellow Disease (`Class ID 0` vs `Class ID 1`):**
   - Karena tidak tersedianya file `data.yaml` pada repositori asli, diperlukan sampling visual untuk memastikan apakah Class 1 konsisten mewakili klorosis daun dan Class 0 mewakili daun normal, atau apakah terdapat kelas ketiga yang hilang.

2. **Status Spesimen Mawar Alami Tanpa Penyakit (`Rosa / Rosa` — 230 file):**
   - Sebanyak 230 gambar pada subfolder `Rosa/Rosa` saat ini dikarantina (`quarantined`) karena nama folder tidak mencantumkan status sehat/sakit. Diperlukan inspeksi visual singkat untuk memutuskan apakah 230 gambar ini dapat digabungkan ke `Rose - Healthy` atau tetap sebagai unlabelled specimen.

---
*Laporan ini dihasilkan oleh skrip `scripts/build_canonical_dataset_stage5.py` secara otomatis dan non-destruktif.*
