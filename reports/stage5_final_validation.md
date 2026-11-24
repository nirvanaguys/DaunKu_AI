# Laporan Audit Validasi Akhir: Stage 5 Canonical Dataset DaunKu AI

> **Waktu Audit:** 2026-11-24 10:28:43  
> **Status Audit:** **VALID & VERIFIED (Konsistensi 100% Tercapai)**  
> **Peran:** Senior Machine Learning Engineer & Data Auditor  
> **Dasar Audit:** `artifacts/canonical_manifest.csv`, `configs/label_mapping.yaml`, `reports/canonical_dataset_design.md`, `reports/potential_data_leakage.csv`  

---

## 1. Ringkasan Eksekutif Hasil Validasi

Audit validasi independen telah dilakukan terhadap seluruh deliverable Tahap 5 proyek DaunKu AI. Audit membuktikan bahwa seluruh artefak kanonikal mematuhi batasan non-destruktif (**Dataset 100% READ-ONLY**, tidak ada modifikasi gambar asli, tidak ada pelatihan model, dan tidak ada physical split).

### Temuan Kunci Audit:
1. **Integritas Manifest:** Tepat **85.022 baris data** dengan **85.022 path relatif unik**. Tidak ada duplikasi baris atau file yang hilang.
2. **Kepatuhan Taksonomi Tripartit:** Sebanyak **43.667 gambar berstatus `Unknown` terbukti 0% dipetakan ke `Healthy`**. True Healthy (**8.810 gambar**) terisolasi secara ketat dari kondisi tidak berlabel.
3. **Pemisahan Status:** `mapping_status` (keabsahan label) terpisah secara independen dari `usage_status` (kelayakan operasional task).
4. **Validasi DSU Parent Grouping:**
   - Terbentuk **31.997 cluster induk independen** (`parent_source_group_id`).
   - Seluruh **12.360 gambar augmentasi Leaf Image Dataset 100,0% terpetakan** ke 1.545 foto aslinya (0 orphan).
   - Seluruh **7.220 exact duplicate groups** terbukti 100% menyatu dalam satu parent group yang sama (0 group split).
   - Seluruh **50 file mawar konflik label** (10 SHA-256 unik) terisolasi penuh dalam status `quarantined`.
   - Sebanyak **689 foto Marigold berlatar alami** (2.067 file instance) terisolasi penuh (`natural_background_holdout`) dengan **0 overlap** terhadap kandidat data training.
5. **Rekonsiliasi 1.280 Pasangan Leakage:** Sebanyak **401 pasangan** telah disatukan oleh DSU (100 exact duplicate + 299 derived Roboflow + 2 dHash=0), sedangkan **879 pasangan** diklasifikasikan sebagai *unverified candidate near-duplicate pairs* yang memerlukan inspeksi visual sebelum physical split.

---

## 2. AUDIT A: Rekonsiliasi Manifest & Status Aktual

### Tabel Rekonsiliasi Status Mapping (`mapping_status`)
| Status Mapping | Jumlah Gambar Manifest Aktual | Persentase | Definisi & Karakteristik Data | Status Kepatuhan |
| :--- | :---: | :---: | :--- | :---: |
| **`mapped`** | **54.200** | 63,75% | Label dengan makna botani/patologi definitif dan terverifikasi | ✅ VERIFIED |
| **`excluded_from_task`** | **24.461** | 28,77% | Subset 100% redundan (`Houseplants`, `v1i`, `Compressed Rubber`, `Rose And Marigold 1`, 12.360 augmentasi statis, dan background) | ✅ VERIFIED |
| **`provisional`** | **5.095** | 5,99% | Dataset *Yellow Disease* tanpa dokumentasi resmi `data.yaml` | ✅ VERIFIED |
| **`ambiguous`** | **1.216** | 1,43% | Gejala tahap awal melati (`Initial stage`: 726), spesimen taksa tanpa label penyakit (`Rosa/Rosa`: 230, `Tagetes/Tagetes`: 213, `Hibiscus/Hibiscus`: 44), strip kosong (`-`: 3) | ✅ VERIFIED |
| **`label_conflict`** | **50** | 0,06% | 10 foto mawar identik biner yang diklaim ganda (*Pest Damage* vs *Rose Mosaic Virus*) | ✅ VERIFIED |
| **`unmapped`** | **0** | **0,00%** | Seluruh file memiliki aturan taksonomi terdaftar | ✅ VERIFIED |
| **TOTAL** | **85.022** | **100,00%** | **Tepat 85.022 file unik** | ✅ VERIFIED |

### Tabel Rekonsiliasi Status Penggunaan (`usage_status`)
| Status Penggunaan | Jumlah Gambar Manifest Aktual | Persentase | Definisi Alokasi Pemodelan |
| :--- | :---: | :---: | :--- |
| **`included`** | **50.082** | 58,90% | Memenuhi syarat kelayakan untuk satu atau lebih task model AI DaunKu |
| **`excluded_from_task`** | **26.512** | 31,18% | Redundan biner atau augmentasi berulang yang dilarang masuk evaluasi |
| **`pending_review`** | **5.095** | 5,99% | Dataset *Yellow Disease* (menunggu konfirmasi visual ahli) |
| **`natural_background_holdout`** | **2.067** | 2,43% | Foto Marigold berlatar alami kebun (689 foto asli beserta salinannya) |
| **`quarantined`** | **1.266** | 1,49% | Mawar konflik (50), `Initial stage` (726), dan folder spesimen ambigu (490) |
| **TOTAL** | **85.022** | **100,00%** | **Tepat 85.022 file unik** |

### Tabel Rekonsiliasi Kondisi Kesehatan Tanaman (`plant_condition`)
| Kondisi Kesehatan | Jumlah Gambar | Persentase | Keterangan Verifikasi Kepatuhan |
| :--- | :---: | :---: | :--- |
| **`Unknown`** | **43.667** | 51,36% | Berasal dari dataset spesies murni (`goletplant`, `Houseplants`, `Kopi`, tanaman v3i tanpa anotasi penyakit, Yellow Disease Class 0). **Terbukti 0 file yang berubah menjadi Healthy.** |
| **`Unhealthy`** | **32.545** | 38,28% | Daun bergejala infeksi patogen jamur/bakteri/virus, stres hara, atau serangan hama. |
| **`Healthy`** | **8.810** | 10,36% | Kontrol pembanding daun sehat terverifikasi dari dataset sayur, bunga, dan perkebunan. |
| **TOTAL** | **85.022** | **100,00%** | Seluruh data tripartit konsisten |

---

## 3. AUDIT B: Evaluasi Implementasi DSU & Parent Grouping

### 1. Metrik Komponen DSU:
- **Total Cluster Induk (`parent_source_group_id`):** **31.997 cluster**.
- **Distribusi Ukuran Cluster:**
  - Cluster ukuran minimum: **1 gambar** (9.296 cluster foto tunggal/independen).
  - Cluster ukuran maksimum: **30 gambar** (cluster mawar yang memuat salinan lintas 3 dataset).
  - Rata-rata ukuran cluster: **2,66 gambar/cluster** (median = 3 gambar).
  - Cluster jamak (>1 gambar): **22.701 cluster** (mencakup 75.726 gambar).

### 2. Validasi Hubungan Kelompok:
- **Exact Duplicate Groups:** Seluruh **7.220 kelompok duplikat biner** terbukti memiliki parent yang sama (**0 kelompok terpecah lintas parent**).
- **Leaf Image Dataset:**
  - Foto asli (`resize plant_leaves dataset`): **1.545 foto**.
  - Foto augmentasi (`augmentation dataset`): **12.360 foto**.
  - Augmentasi yang berhasil dipetakan ke parent foto asli: **12.360 / 12.360 (100,00%)**.
  - Augmentasi tanpa parent / orphan: **0 foto (0,00%)**.
- **Natural Background Holdout vs Training Candidates:**
  - Terbentuk **689 cluster holdout** berlatar alami.
  - Overlap cluster holdout dengan data berstatus `included`: **0 cluster (0,00%)**.
- **Mawar Berlabel Ganda Konflik:**
  - Seluruh **50 file instance mawar konflik** terkumpul dalam **10 cluster parent** yang seluruh anggotanya berstatus `quarantined`.

> [!WARNING]
> **Koreksi Asumsi Zero Leakage:** Keberadaan DSU membuktikan bahwa data yang *diikutsertakan dalam relasi* (exact duplicates, augmentasi Roboflow berbasis nama dasar, dan augmentasi Leaf Image) telah terikat sempurna. Namun, DSU **belum memasukkan pasangan near-duplicate perceptual (dHash)**. Oleh karena itu, klaim 'nol leakage mutlak' hanya berlaku setelah 879 pasangan potential leakage diverifikasi secara visual pada Tahap 6.

---

## 4. AUDIT C: Rekonsiliasi 1.280 Pasangan Potential Data Leakage

Berdasarkan audit komparatif antara hasil Tahap 3.1 (`reports/potential_data_leakage.csv`) dan manifest kanonikal Tahap 5:

### 1. Karakteristik Pasangan Potential Leakage:
- **Asal Data:** 1.280 pasangan ini merupakan **hasil audit yang sama dari Tahap 3.1** yang dihasilkan melalui pemindaian perceptual hash (*difference hash* / dHash) lintas-split pada dataset yang telah memiliki train/valid/test bawaan (`goletplant`, `Houseplants`, `Kopi`, `v1i`, `v3i`).
- **Distribusi Risiko:**
  - **HIGH Risk:** **537 pasangan** (terdiri dari 100 pasangan exact duplicate biner, 299 varian turunan Roboflow dari foto dasar yang sama, 50 pasangan dHash = 0, dan 88 pasangan dHash = 1).
  - **MEDIUM Risk:** **743 pasangan** (terdiri dari 222 pasangan dHash = 2 dan 521 pasangan dHash = 3).
- **Perbedaan Ambang Batas dHash:**
  - Ambang batas $dHash \le 1$ mendeteksi duplikasi identik atau gambar dengan perbedaan kompresi mikroskopis.
  - Ambang batas $dHash \le 10$ menangkap variasi augmentasi geometris (rotasi ringan, crop, fluktuasi pencahayaan).

### 2. Status Penanganan dalam DSU Tahap 5:
- **Terserap dalam DSU (401 pasangan):**
  - Sebanyak **100 pasangan exact duplicate** otomatis disatukan oleh DSU exact hash.
  - Sebanyak **299 pasangan Roboflow base-image** otomatis disatukan oleh DSU pola penamaan `_jpg.rf.hash`.
  - Sebanyak **2 pasangan dHash = 0** telah memiliki korelasi biner.
  - *Hasil:* 401 pasangan ini terbukti **berada dalam `parent_source_group_id` yang sama** sehingga dijamin tidak akan bocor saat splitting baru.
- **Belum Masuk DSU (879 pasangan — Unverified Candidate Near-Duplicates):**
  - Sebanyak **879 pasangan** (48 dHash=0, 88 dHash=1, 222 dHash=2, 521 dHash=3) saat ini berada pada parent berbeda karena DSU Tahap 5 sengaja membatasi diri pada hubungan yang terbukti secara deterministik (bukan kemiripan perkiraan).
  - *Rekomendasi:* Pasangan ini diklasifikasikan sebagai **`potential leakage pairs`** dan wajib dilakukan sampling visual pada Tahap 6 sebelum penetapan split final.

---

## 5. AUDIT D: Evaluasi Kelayakan Task AI (Task Eligibility)

Hitungan kelayakan dihitung berdasarkan **jumlah gambar unik**, bukan jumlah label atau baris aturan:

| No | Task Pemodelan AI | Eligible Images | Ineligible Images | Unknown Labels | Quarantined | Holdout | Alasan Eksklusi Utama |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | **Plant Species Identification** | **51.532** | 33.490 | 5.095 | 53 | 0 | Eksklusi subset 100% redundan (`Houseplants`, `v1i`, `Compressed Rubber`), foto background tanpa tanaman, dan Yellow Disease (spesies belum diketahui). |
| **2** | **Plant Condition Classification** | **20.164** | 64.858 | 43.667 | 540 | 0 | Eksklusi 43.667 gambar berlabel `Unknown` (goletplant, kopi, dll), mawar berlabel ganda konflik, dan subset duplikat redundan. |
| **3** | **Disease/Symptom Diagnosis** | **19.438** | 65.584 | 43.667 | 1.266 | 0 | Eksklusi seluruh dataset tanpa diagnosis patogen spesifik (Kopi hanya berlabel 'leaf', goletplant hanya spesies, Yellow Disease provisional, dan Jasmine `Initial stage`). |
| **4** | **Leaf/Object Detection (BBox)** | **37.070** | 47.952 | 0 | 1.266 | 0 | Eksklusi dataset klasifikasi berbasis folder biasa yang tidak memiliki koordinat bounding box (Tomat, Kentang, Melati, Karet, Mawar, Leaf Image). |

### Verifikasi Kepatuhan Khusus:
1. **Dataset Daun Kopi (`Klasifikasi Penyakit Daun Kopi.v4i`):**
   - Masuk ke Disease Diagnosis: **0 gambar (0,00%)** ✅
   - Masuk ke Leaf Detection: **3.139 gambar (100,00% dari data ber-bounding box)** ✅
   - Gambar background tanpa bounding box (77 gambar) berstatus `ineligible` untuk seluruh task ✅
2. **Dataset Yellow Disease (`A dataset of Yellow Disease in Horticultural Plant`):**
   - Status: **5.095 gambar berstatus `provisional` dan `pending_review`** ✅
   - Masuk ke Disease Diagnosis: **0 gambar (0,00%)** ✅
   - Masuk ke Leaf Detection: **5.095 gambar (koordinat YOLO valid)** ✅
3. **Rose Mosaic Virus pada Hibiscus:**
   - Masuk ke evaluasi mawar maupun kembang sepatu: **0 gambar** (aturan `suspected_mislabel` memblokir seluruh potensi evaluasi) ✅
4. **Initial Stage Jasmine:**
   - Masuk ke Disease Diagnosis: **0 gambar** (dikarantina karena belum spesifik) ✅
   - Masuk ke Condition Classification: **726 gambar** (terverifikasi sebagai daun sakit / `Unhealthy`) ✅
5. **Background-Only Images:**
   - Masuk ke Disease Diagnosis maupun Species ID: **0 gambar** ✅

---

## 6. AUDIT E: Rekonsiliasi Natural Background & Karantina

### 1. Foto Marigold Berlatar Alami (689 Foto vs 2.067 File Instance):
- **Foto Dasar Unik:** **689 foto** yang diambil di kebun alami (338 *Alternaria*, 273 *Healthy*, 78 *Pest Damage*).
- **Sebaran File Instance Lintas-Dataset:**
  - `dataset for various disease detection...`: **689 file instance**
  - `Perfect Data Set`: **689 file instance** (salinan biner identik)
  - `Rose And MArigold Leaf Disease 1`: **689 file instance** (salinan biner identik)
  - **Total File Instance:** **2.067 file**.
- **Status Audit:** Ketiga set salinan ini terikat ke dalam **689 parent cluster yang sama**. Seluruh 2.067 baris manifest ditandai sebagai `usage_status = natural_background_holdout` sehingga **tidak akan dihitung sebagai sampel independen ganda**.

### 2. Mawar Berlabel Ganda Konflik (10 Foto vs 50 File Instance):
- **Foto Dasar Unik:** **10 foto** yang memiliki konflik label biner (*Pest Damage* vs *Rose Mosaic Virus*).
- **Sebaran File Instance Lintas-Dataset:**
  - `Perfect Data Set`: **20 file instance** (10 di folder hama, 10 di folder virus).
  - `Rose And MArigold Leaf Disease 1`: **20 file instance** (10 di folder hama, 10 di folder virus).
  - `dataset for various disease detection...`: **10 file instance** (di folder mawar).
  - **Total File Instance:** **50 file**.
- **Status Audit:** Seluruh 50 baris manifest berstatus `mapping_status = label_conflict` dan `usage_status = quarantined` dengan kelayakan seluruh task `False`.

### 3. Folder Spesimen Ambigu (490 Gambar):
- `Rosa / Rosa`: **230 gambar** (foto mawar berlatar alami tanpa keterangan sehat/sakit).
  - Terbukti **0 gambar** yang dipetakan ke `Healthy`. Kondisi tercatat **`Unknown`** dan status `quarantined`.
- `Tagetes erecta / Tagetes`: **213 gambar** (foto marigold tanpa keterangan sehat/sakit). Kondisi tercatat **`Unknown`** dan status `quarantined`.
- `Hibiscus rosa-sinensis / Hibiscus rosa-sinensis`: **44 gambar** (foto kembang sepatu tanpa keterangan penyakit). Kondisi tercatat **`Unknown`** dan status `quarantined`.
- `goletplant` strip kosong (`-`): **3 gambar** (anotasi bounding box cacat). Status `quarantined`.
- **Total Spesimen Ambigu:** 230 + 213 + 44 + 3 = **490 gambar**.

### 4. Jasmine Gejala Awal (`Initial stage`):
- Sebanyak **726 gambar** berstatus `mapping_status = ambiguous` dan `usage_status = quarantined` untuk klasifikasi penyakit spesifik.

---

## 7. Status Keputusan Pengguna & Batasan Validasi

| No | Keputusan Pengguna | Status Implementasi | Bukti Artefak |
| :-: | :--- | :---: | :--- |
| 1 | Exclude 10 foto mawar konflik dari supervised training/validation | **SELESAI (100%)** | 50 file instance ditandai `label_conflict` dan `quarantined` di `canonical_manifest.csv`. |
| 2 | Exclude Daun Kopi dari disease diagnosis, izinkan untuk leaf detection | **SELESAI (100%)** | `eligible_disease_diagnosis=False`, `eligible_leaf_detection=True`, kondisi `Unknown`. |
| 3 | Rose Mosaic Virus pada Hibiscus ditandai suspected_mislabel | **SELESAI (100%)** | Aturan `suspected_mislabel` aktif di `label_mapping.yaml`, audit membuktikan folder tidak ada di dataset fisik. |
| 4 | Yellow Disease tetap provisional & pending review | **SELESAI (100%)** | 5.095 gambar berstatus `provisional` dan `pending_review`, dieksklusikan dari diagnosis spesifik. |
| 5 | Group-Aware split berbasis parent_source_group_id | **SELESAI (100%)** | 31.997 cluster terbentuk via DSU, augmentasi Leaf Image 100% terpetakan, 0 duplicate split. |
| 6 | 689 Mawar/Marigold alami ditandai natural_background_holdout | **SELESAI (100%)** | 2.067 file instance ditandai `natural_background_holdout` dengan 0 overlap data latih. |
| 7 | Harmonisasi taksonomi botani (28 taksa acuan + 52 goletplant) | **SELESAI (100%)** | Nama ilmiah dinormalisasi, variasi kapitalisasi dan sinonim disatukan. |

### Batasan Validasi yang Harus Diperhatikan:
1. **879 Pasangan Potential Leakage Belum Terverifikasi:** Pasangan ini belum dimasukkan ke DSU karena membutuhkan audit visual manual untuk membedakan antara variasi sudut kamera (*true near-duplicate*) dengan daun bertekstur mirip (*false positive*).
2. **Ketiadaan data.yaml Yellow Disease:** Tanpa verifikasi ground truth visual dari ahli patologi, Class ID 0 dan 1 tidak boleh digunakan untuk klaim performa model penyakit.

---
*Laporan audit validasi ini disusun oleh Senior Machine Learning Engineer & Data Auditor secara independen dan berbasis data aktual.*
