# Laporan Rekomendasi Arsitektur Model AI (Stage 7 — Final Integrated Revision) — DaunKu AI

> **Tanggal Revisi Final:** 25 November 2026  
> **Status:** Rancangan Arsitektur Final — Menunggu Persetujuan sebelum Stage 8 (**Bukan Tahap Training**)  
> **Peran:** Senior Machine Learning Engineer, AI Architect, & Computer Vision Specialist  
> **Artefak Kebenaran Acuan:**  
> - `daunku_ai/artifacts/splits/split_manifest.csv` (85.022 baris)  
> - `daunku_ai/artifacts/splits/train_manifest.csv` (51.120 baris), `validation_manifest.csv` (14.850 baris), `test_manifest.csv` (14.748 baris)  
> - `daunku_ai/artifacts/splits/split_config.yaml` & `split_summary.json`  
> - `daunku_ai/artifacts/canonical_manifest.csv` & `daunku_ai/configs/label_mapping.yaml`  
> - `daunku_ai/reports/canonical_dataset_design.md`, `stage5_final_validation.md`, `stage6_1_final_integrity_review.md`, `environment_audit.md`  
> - `daunku_ai/Rencana_Implementasi_AI_DaunKu.md`

---

## 1. Ringkasan Eksekutif

Dokumen ini merupakan rancangan arsitektur final terpadu Tahap 7 untuk **DaunKu AI**. Seluruh angka jumlah gambar, definisi kelas, temuan *cross-task leakage*, dan keputusan arsitektur telah diverifikasi langsung terhadap artefak Stage 5 dan Stage 6 tanpa memodifikasi dataset asli (`Dataset/`), aplikasi Flutter (`daunku_app/`), manifest, label mapping, maupun split Stage 6.

### Prinsip Inti Arsitektur:
1. **Modular Multi-Task dengan *Species-Aware Gating* (Bukan Monolitik & Bukan *Hard Top-1 Masking*):**  
   Identifikasi spesies, klasifikasi kondisi, diagnosis penyakit/gejala, dan deteksi objek dipisahkan sebagai task independen. Penggabungan keputusan menggunakan eksperimen terukur (*unmasked baseline*, *Top-2*, *Top-3*, *soft species prior*, dan *low-confidence fallback*), bukan *hard masking* berbasis Top-1 semata.
2. **Full-Image Classification sebagai Baseline Utama; ROI Crop sebagai Eksperimen Tambahan:**  
   Karena anotasi bounding box tidak mencakup seluruh spesies dan memiliki semantik heterogen (tanaman utuh, daun kopi, area gejala), klasifikasi *full-image* ditetapkan sebagai baseline utama. *ROI crop* hanya boleh digunakan dalam eksperimen tambahan dengan protokol training/evaluasi yang konsisten untuk mencegah *distribution shift*.
3. **Audit Transparan terhadap *Cross-Task Leakage*:**  
   Setiap task secara individual memiliki **zero known/audited leakage pairs across splits** (intra-task), namun audit lintas-task membuktikan adanya **tumpang tindih split antar-task** karena pembagian Stage 6 dilakukan terpisah per task. Oleh karena itu, **baseline pertama dijalankan per-task (intra-task)** dengan mempertahankan split Stage 6 sebagai baseline historis; **OOF calibration berstatus *deferred*** (bukan persyaratan baseline pertama) sampai protokol *nested training* dan *calibration* divalidasi.
4. **Status Implementasi Jujur:**  
   Seluruh kandidat model (`EfficientNet-B0`, `MobileNetV3-Small`, `MobileNetV3-Large`, `ResNet50`, `YOLOv8n`, `YOLO11n`) masih berstatus **rekomendasi arsitektur**, belum dilatih dan belum diuji. **FastAPI**, **ONNX**, **TFLite**, **Knowledge Base**, dan integrasi **Flutter (`daunku_app`)** berstatus **rancangan konseptual** (Tahap 10–13) dan belum diimplementasikan.

---

## 2. Verifikasi Jumlah Data & Definisi Kelas per Task AI

Seluruh angka di bawah ini diverifikasi langsung dari `artifacts/splits/split_manifest.csv`, `split_summary.json`, `canonical_manifest.csv`, dan `configs/label_mapping.yaml`.

### Tabel Rekapitulasi Verifikasi Data Aktif

| Task Pemodelan AI | Train | Validation | Test (Locked) | Total Aktif | Definisi & Jumlah Kelas Aktual | Kelas Tanpa Validation | Kelas Tanpa Test |
| :--- | ---: | ---: | ---: | ---: | :--- | :---: | :---: |
| **1. Species Identification** | 37.500 *(68-cls: 37.408)* | 6.068 *(68-cls: 6.068)* | 6.062 *(68-cls: 6.047)* | **49.630** *(68-cls: **49.523**)* | **105 label aktif** = **68 single-species** (baseline utama: 49.523 gambar, 25.930 `meta_component_id`) + **37 kombinasi multi-spesies** (107 gambar, 43 `meta_component_id`) | **37** *(semua multi-spesies)* | **32** *(semua multi-spesies)* |
| **2. Condition Classification** | 13.109 | 2.799 | 2.841 | **18.749** | **2 kelas** (`Healthy` 18,51% vs `Unhealthy` 81,49%, rasio 1 : 4,40) | **0** | **0** |
| **3. Disease/Symptom Diagnosis** | 13.107 | 2.788 | 2.854 | **18.749** | **53 label aktif** = **47 gejala tunggal/utama** + **6 kombinasi multi-gejala** | **3** *(multi-gejala)* | **3** *(multi-gejala)* |
| **4. Object / Leaf Detection** | 27.600 | 4.888 | 4.582 | **37.070** | **72 kelas bbox atomik** (**70 terverifikasi** + **2 `Yellow Disease` provisional**) / **154 kombinasi gambar** | **0 atomik** / 67 komb. | **0 atomik** / 53 komb. |

---

### A. Task 1: Plant Species Identification
* **Rekonsiliasi 103 vs 105 Kelas:**
  - `configs/label_mapping.yaml` memiliki **106** `plant_species` unik dengan `task_eligibility.species_id = true`.
  - Setelah `Marigold (Tagetes erecta)` diisolasi ke `natural_background_holdout` (689 foto dasar / 2.067 file instance), tersisa **105 label `plant_species` aktif** berstatus `included` yang terverifikasi identik di `split_manifest.csv` dan `split_summary.json`.
  - Angka **103 kelas** yang tercatat pada teks `reports/stage6_1_final_integrity_review.md` merupakan ketidaksesuaian penulisan narasi laporan teks Stage 6.1 terhadap artefak data aktual (105 label). Laporan Stage 6.1 tidak diubah secara otomatis dan dicatat sebagai temuan audit.
* **Pemisahan Single-Species vs Combination Labels (WAJIB — Terverifikasi Langsung dari Manifest):**
  - **Baseline Utama — 68 kelas single-species (49.523 gambar unik | 25.930 `meta_component_id` unik):**
    - **Train:** **37.408 gambar unik** (**19.447** `meta_component_id` unik; 68 kelas).
    - **Validation:** **6.068 gambar unik** (**3.241** `meta_component_id` unik; 68 kelas).
    - **Test (Locked):** **6.047 gambar unik** (**3.242** `meta_component_id` unik; 68 kelas).
    - **Distribusi Kelas 68 Single-Species (*verified from manifest*):** Min = **52 gambar** (`Dracaena angolensis`: Tr 44 [16 mc] / Val 4 [2 mc] / Te 4 [2 mc]), Median = **491,5**, Mean = **728,3**, Max = **5.589** (`Arabian Jasmine`: Tr 4.254 / Val 692 / Te 643). Seluruh 68 kelas hadir di Train, Validation, dan Test, **namun tidak seluruh 68 kelas memiliki kekuatan evaluasi yang setara** — khususnya `Dracaena angolensis` hanya memiliki **2 `meta_component_id` (4 gambar)** pada Validation dan **2 `meta_component_id` (4 gambar)** pada Test sehingga estimasi metrik per kelasnya bervarians tinggi dan harus dilaporkan dengan catatan kehati-hatian.
  - **Dieksklusikan dari Baseline 68-Class Softmax — 37 label kombinasi multi-spesies (107 baris = 107 gambar unik | 43 `meta_component_id` unik):**
    - **Train:** **92 gambar** (37 `meta_component_id`, 37 kelas) | **Validation:** **0 gambar** (0 kelas) | **Test (Locked):** **15 gambar** (6 `meta_component_id`, 5 kelas).
    - *Rekonsiliasi Penuh (*verified from manifest*):* Unit hitung **49.523** adalah **baris manifest = `image_id` unik = `relative_path` unik** (terdiri dari **26.255** `parent_source_group_id` unik dan **25.930** `meta_component_id` unik). $49.523 + 107 = \mathbf{49.630}$ gambar unik (`Train`: $37.408 + 92 = 37.500$; `Val`: $6.068 + 0 = 6.068$; `Test`: $6.047 + 15 = 6.062$; 0 duplikasi hitung).
    - *Hubungan 8 `meta_component_id` bersama:* Terdapat **8 `meta_component_id`** yang memuat baik gambar single-species maupun gambar kombinasi multi-spesies, seluruhnya berasal dari `goletplant.v5i.tensorflow` (**6 komponen di `train`**: `COMP_09145`, `COMP_13902`, `COMP_13936`, `COMP_14104`, `COMP_14118`, `COMP_14174`; **2 komponen di `test`**: `COMP_14103`, `COMP_14120`; **0 lintas-split**).
  - **Keputusan Desain (*design recommendation*):** 68 single-species dan 37 combination labels **tidak boleh digabung menjadi satu softmax 105 kelas**. Baseline utama Task 1 menggunakan **68 kelas single-species** (`CrossEntropyLoss` pada 49.523 gambar), sedangkan 37 label kombinasi (107 gambar) dievaluasi terpisah tanpa mengubah anotasi asli maupun split Stage 6.

### B. Task 2: Plant Condition Classification
* **Distribusi Aktual (Tidak Seimbang — Imbalance 1 : 4,40):**
  - **Train (13.109):** `Healthy` = **2.439 (18,61%)** | `Unhealthy` = **10.670 (81,39%)** *(1 : 4,37)*.
  - **Validation (2.799):** `Healthy` = **504 (18,01%)** | `Unhealthy` = **2.295 (81,99%)** *(1 : 4,55)*.
  - **Test (2.841, Locked):** `Healthy` = **528 (18,59%)** | `Unhealthy` = **2.313 (81,41%)** *(1 : 4,38)*.
  - **Total Aktif (18.749):** `Healthy` = **3.471 (18,51%)** | `Unhealthy` = **15.278 (81,49%)** *(1 : 4,40)*.
  - **Data `Unknown`:** 43.667 gambar pada `canonical_manifest.csv` diisolasi penuh dari task ini.
* **Strategi Penanganan Imbalance:** Wajib menggunakan class-weighted `BCEWithLogitsLoss` (bobot proporsional rasio Train ~4,37 untuk kelas minoritas `Healthy`), pembanding *WeightedRandomSampler* / *Focal Loss*, serta evaluasi berbasis **Balanced Accuracy, Macro F1, PR-AUC, Sensitivity, Specificity, dan Subgroup Accuracy per spesies**.

### C. Task 3: Disease/Symptom Diagnosis
* **Verifikasi Kelas & Struktur Anotasi:**
  - **53 kelas aktif** (Train: 53, Validation: 50, Test: 50): **50 kelas muncul di seluruh split**, dan **3 kelas bersifat train-only** (tidak ada di Validation maupun Test):
    1. `Dehydration / Under-watering + Leaf Curl (Abiotic / Viral)` (3 gambar, Train only).
    2. `Dehydration / Under-watering + Leaf Curl (Abiotic / Viral) + Over-watering / Root Rot Indication` (3 gambar, Train only).
    3. `Over-watering / Root Rot Indication + Rust (Pucciniales)` (1 gambar, Train only).
  - **Verifikasi Sumber & Unit Hitung (*verified from manifest*):**
    - `classification_folder`: **17.870 baris = 17.870 `image_id` unik = 17.870 `relative_path` unik** (14.360 `parent_source_group_id` unik; 14.360 `meta_component_id` unik).
    - `bbox_tensorflow_csv` (`v3i`): **879 baris = 879 `image_id` unik = 879 `relative_path` unik** (334 `parent_source_group_id` unik; 333 `meta_component_id` unik), memuat **6 label kombinasi multi-gejala** (total **113 gambar**: 3 kelas muncul di semua split [`Dehydration + Sunburn`: 51; `Over-watering + Sunburn`: 48; `Dehydration + Over-watering`: 7] dan 3 kelas train-only di atas).
    - **Overlap antara `classification_folder` dan `bbox_tensorflow_csv`:** **0 `image_id`**, **0 `relative_path`**, **0 `parent_source_group_id`**, dan **0 `meta_component_id`**. Sehingga $17.870 + 879 = \mathbf{18.749}$ terbukti sebagai **jumlah gambar unik saling lepas** (14.694 `parent_source_group_id`, 14.693 `meta_component_id`).
    - *Catatan Interpretasi:* Ketiadaan label sekunder pada anotasi `classification_folder` **tidak boleh disimpulkan** bahwa gejala lain pasti tidak ada pada foto tersebut.
* **Unresolved Design Decision — Multiclass vs Multi-Label:**
  - **Status:** `UNRESOLVED`.
  - **Alasan:** Data `v3i` (879 gambar) menunjukkan bahwa gejala tidak selalu *mutually exclusive*, sedangkan 17.870 gambar `classification_folder` hanya menyediakan 1 label per gambar tanpa bukti bahwa gejala sekunder absen. Selain itu, masih terdapat fragmentasi label sumber (`Healty leaf` 82 gambar vs `None (Healthy)` 3.471 gambar; variasi ejaan seperti `Leaf curll`, `Yelllow Mosaic virus`).
  - **Bukti yang Dibutuhkan:** Audit eksperimen awal Stage 8 membandingkan *multiclass* (pada kelas gejala tunggal terwakili) vs *multi-label sigmoid* (dengan pemetaan gejala atomik untuk `v3i`), serta keputusan formal atas konsolidasi label sinonim.
  - **Dampak pada Stage 8:** Baseline utama dimulai dengan formulasi *multiclass* pada kelas tunggal yang hadir di seluruh split (dengan 6 label kombinasi dilaporkan terpisah), sambil menyiapkan eksperimen pembanding *multi-label* untuk subset gejala ganda.

### D. Task 4: Object / Leaf Detection
* **Rekonsiliasi Sumber Data (goletplant 26.006 vs 26.063 & v3i 2.830 vs 2.773):**
  - Verifikasi langsung pada `split_manifest.csv` membuktikan angka **aktif & eligible** adalah:
    - `goletplant.v5i.tensorflow`: **26.006 aktif** (dari total manifest 26.063; **54** berstatus `excluded_from_task` / `not_in_task` dan **3** `quarantined` karena anotasi strip `-`).
    - `Plant Classification and Disease.v3i.tensorflow`: **2.830 aktif** (dari total manifest 3.184; **354** berstatus `excluded_from_task` / `not_in_task`).
    - `Klasifikasi Penyakit Daun Kopi.v4i.tensorflow`: **3.139 aktif** (dari total manifest 3.216; **77** background `not_in_task`).
    - `A dataset of Yellow Disease in Horticultural Plant`: **5.095 aktif** *(status `provisional` / `pending_review`)*.
    - **Total Aktif:** $26.006 + 2.830 + 3.139 + 5.095 = \mathbf{37.070}$ **gambar**.
  - *Penyebab selisih dokumen lama:* Dokumen Stage 7 awal secara keliru memakai total mentah `goletplant` (26.063) lalu mengurangkan selisih 57 gambar ke `v3i` ($2.830 - 57 = 2.773$). Angka yang benar dan sah berdasarkan manifest adalah **26.006 (`goletplant`)** dan **2.830 (`v3i`)**.
* **Rekonsiliasi Jumlah Kelas Detection (149 vs 154 vs 72 vs 70+2 — *verified from manifest*):**

| Definisi Kelas Detection | Jumlah Kelas | Distribusi Split (Tr / Val / Te) | Kelas Hilang per Split | Sumber Verifikasi | Status |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Image-level label combinations** (`canonical_label` / `original_label`) | **154** *(151 `included` + 3 `Yellow`)* | **153 / 87 / 101** | 1 hilang di Train (kombinasi 5-spesies di Test); 67 hilang di Val; 53 hilang di Test | `split_manifest.csv`, `split_summary.json`, `label_mapping.yaml` | *Verified from manifest* |
| **Atomic bbox classes (semua 4 sumber)** — pemecahan delimiter `' + '` | **72** | **72 / 72 / 72** | **0** hilang di Train, Val, maupun Test | `split_manifest.csv` | *Verified from manifest* |
| **Atomic bbox terverifikasi (Non-Yellow — Baseline 4A)** | **70** *(52 Plant Species + 10 Plant Object + 7 Symptom + 1 Coffee Leaf)* | **70 / 70 / 70** | **0** hilang (min `meta_component`: Tr=15, Val=3, Te=2 pada `Dracaena angolensis - Plant Object`) | `split_manifest.csv` (31.975 gambar: Tr 23.791 / Val 4.251 / Te 3.933) | *Verified from manifest* |
| **Atomic bbox `Yellow Disease` provisional (Sub-eksperimen 4B)** | **2** (`Class 0`, `Class 1`) | **2 / 2 / 2** | **0** hilang (0 overlap dengan 70 kelas terverifikasi) | `split_manifest.csv` (5.095 gambar: Tr 3.809 / Val 637 / Te 649) | *Verified provisional (pending_review)* |
| **Klaim teks Stage 6.1 (`149 kelas`, `50 rare classes`)** | **149** *(legacy textual claim)* / **50** *(rare)* | Tidak diturunkan secara terprogram di `audit_stage6_1_integrity.py` | `50` cocok dgn `rare_classes` di `split_summary.json`; angka **149** berstatus **`legacy textual claim` yang belum dapat direkonsiliasi** terhadap 154, 151, 72, maupun 70 | `reports/stage6_1_final_integrity_review.md` | *Unresolved legacy textual discrepancy (tidak diubah otomatis)* |

  - **Keputusan Baseline (*design recommendation*):** Baseline utama deteksi (**Sub-eksperimen 4A**) hanya menggunakan **70 kelas atomik terverifikasi** (31.975 gambar). **2 kelas `Yellow Disease` (`provisional`) tidak dinyatakan valid untuk baseline utama** dan hanya diuji terpisah pada Sub-eksperimen 4B.

---

## 3. Cross-Task Data Leakage Review (Audit Kritis)

Audit langsung pada `artifacts/splits/split_manifest.csv` terhadap seluruh 4 task (`split_species_id`, `split_condition`, `split_disease_diagnosis`, `split_leaf_detection`) menemukan hal kritis berikut:

### A. Temuan Tumpang Tindih Split Antar-Task (Terverifikasi)
Meskipun masing-masing task secara individual memenuhi **zero known/audited leakage pairs across splits** (intra-task), pembagian Stage 6 dibuat secara independen per task sehingga **gambar dan `meta_component_id` yang sama sering berada di `train` pada satu task dan di `validation`/`test` pada task lain**:

| Pasangan Task | Gambar Aktif Bersama | Task A = `train` & Task B = `val`/`test` (Gambar) | Overlap `meta_component` (A=`train`, B=`val` / `test`) | Task B = `train` & Task A = `val`/`test` (Gambar) | Overlap `meta_component` (B=`train`, A=`val` / `test`) |
| :--- | ---: | ---: | :---: | ---: | :---: |
| **Species ID vs Disease** | 18.534 | **4.173** | 1.648 / 1.626 | **3.170** | 1.237 / 1.303 |
| **Species ID vs Condition** | 18.534 | **4.189** | 1.629 / 1.640 | **3.189** | 1.266 / 1.270 |
| **Condition vs Disease** | 18.749 | **3.964** | 1.533 / 1.557 | **3.962** | 1.528 / 1.558 |
| **Species ID vs Detection** | 31.760 | **5.936** | 1.002 / 1.078 | **5.541** | 1.036 / 1.044 |
| **Condition vs Detection** | 879 | **173** | 31 / 35 | **211** | 36 / 43 |
| **Disease vs Detection** | 879 | **166** | 30 / 37 | **203** | 35 / 41 |

### B. Tumpang Tindih `test` di Satu Task vs `validation` di Task Lain (*verified from manifest*)
Selain overlap `train`-vs-`val`/`test`, audit juga menemukan kelompok yang berstatus **Locked `test` pada satu task tetapi `validation` pada task lain**:
- `split_species_id = test` & `split_disease_diagnosis = validation`: **256 `meta_component_id`** (**312 gambar**).
- `split_species_id = test` & `split_condition = validation`: **289 `meta_component_id`** (**351 gambar**).
- `split_condition = test` & `split_disease_diagnosis = validation`: **330 `meta_component_id`** (**420 gambar**).
- `split_disease_diagnosis = test` & `split_species_id = validation`: **300 `meta_component_id`** (**382 gambar**).
- `split_disease_diagnosis = test` & `split_condition = validation`: **333 `meta_component_id`** (**437 gambar**).
- `split_leaf_detection = test` & `split_species_id = validation`: **178 `meta_component_id`** (**475 gambar**).

**Dampak terhadap Evaluasi Pipeline & Calibration:**  
Jika pipeline gabungan dievaluasi atau di-tuning langsung pada `validation` Disease Diagnosis: (1) >70% gambar telah dilihat model Species ID saat training (*train-to-val leakage*), (2) 256 `meta_component_id` merupakan bagian dari Locked Test Species ID dan 330 `meta_component_id` merupakan bagian dari Locked Test Condition (*indirect test exposure*), dan (3) **OOF pada bobot model saja belum cukup** — calibrator (Temperature Scaling) dan threshold selection yang di-fit menggunakan kelompok evaluasi downstream juga menimbulkan leakage.

### C. Solusi Non-Destruktif (Dua Protokol Terpisah) & Keterbatasan Jujur Split Stage 6
Sesuai aturan proyek, split Stage 6 **tidak diubah secara otomatis**. Prinsip wajib lintas-task: **OOF 5-fold biasa yang hanya mengecualikan fold saat ini belum menjamin seluruh Locked Test Set bebas dari paparan training** (karena fold-$j$ masih dapat melatih pada kelompok test milik fold lain $k \neq j$). Oleh karena itu, protokol dipisahkan secara tegas (*proposed protocol*):

1. **Protokol A — Group-Aware OOF & OOF Calibration (`DEFERRED` — Bukan Persyaratan Baseline Pertama):**  
   OOF calibration **ditunda (*deferred*)** dan **belum siap digunakan** sampai protokol *nested training* dan *calibration* divalidasi. Bila nantinya diaktifkan untuk integrasi multi-model (**Species Identification**, **Condition Classification**, **Disease/Symptom Diagnosis**, serta **Object/Leaf Detection** bila dipakai), OOF menggunakan *group-aware K-fold* ($K=5$, `groups = meta_component_id`, `OOF_SEED = 42`) **hanya pada himpunan training bersih setelah eksklusi himpunan evaluasi** (Protokol B).
2. **Protokol B — Pemisahan Ketat `inner_val` vs `val_cal` vs `val_thresh` vs `E_test` (*Proposed Protocol*):**
   - **Definisi Seragam (*verified/derived* dari `split_manifest.csv`):**
     - `E_test`: gabungan seluruh `meta_component_id` Locked Test lintas-task yang terlibat ($E_{\text{test},3}$ = **6.841 mc** untuk 3 task klasifikasi; $E_{\text{test},4}$ = **8.343 mc** untuk 4 task). `E_test` tetap terkunci sepenuhnya (tidak pernah dipakai untuk training, early stopping, model selection, calibration, maupun threshold selection).
     - `E_val`: gabungan seluruh `meta_component_id` Validation Set lintas-task yang terlibat ($E_{\text{val},3}$ = **6.783 mc**; $E_{\text{val},4}$ = **8.241 mc**).
     - `E_val_clean`: `E_val` setelah mengeluarkan seluruh grup yang overlap dengan `E_test` ($E_{\text{val},3}^{\text{clean}} = E_{\text{val},3} \setminus E_{\text{test},3}$ = **5.250 mc**; $E_{\text{val},4}^{\text{clean}} = E_{\text{val},4} \setminus E_{\text{test},4}$ = **6.302 mc**).
     - `val_cal` dan `val_thresh`: partisi terencana dari `E_val_clean` (*proposed protocol*, **bukan** artefak Stage 6 yang sudah dibuat).
   - **Resolusi Konflik Penggunaan Validation Set (Dua Jalur Model Terpisah):**
     - **Jalur 1 (Model Baseline Per-Task / Intra-Task):** Memisahkan **~15% `inner_val`** (group-aware berdasarkan `meta_component_id`) dari `train` Stage 6 khusus untuk *early stopping* dan *model selection*, sehingga Validation Set Stage 6 tetap steril untuk `val_cal` (Temperature Scaling) dan `val_thresh` (threshold selection).
     - **Jalur 2 (Model Evaluasi Pipeline Gabungan — Protocol B):** Memisahkan **~15% `inner_val`** dari *clean training pool* (di luar `E_val ∪ E_test`) khusus untuk *early stopping*, *model selection*, dan *hyperparameter tuning*. **Base model yang menghasilkan prediksi `val_cal`, `val_thresh`, dan `E_test` tidak boleh pernah menggunakan grup dari `val_cal`, `val_thresh`, maupun `E_test` untuk training, early stopping, model selection, atau hyperparameter tuning.**
   - **Stratifikasi Multi-Task (`Unresolved`):** Metode pembagian/stratifikasi grup lintas task dengan label berbeda (species, condition, disease, bbox) **belum dirancang**; `StratifiedGroupKFold` hanya berlaku pada mode single-task dan tidak diklaim menyelesaikan stratifikasi multi-task.
   - **Total Dampak Penyusutan Training Termasuk 15% `inner_val` (*derived proportional estimate* dari *clean training pool* `split_manifest.csv`):**
     - *Jalur 1 Intra-Task (85% train Stage 6):* Species 68-cls 37.408 → **~31.797 (-15,0%)**; Condition 13.109 → **~11.143 (-15,0%)**; Disease 13.107 → **~11.141 (-15,0%)**; Detection 4A 23.791 → **~20.222 (-15,0%)**.
     - *Jalur 2 Protocol B (eksklusi `E_val ∪ E_test` + 15% `inner_val`):* Species 68-cls 37.408 → **~25.725 (-31,2%, 3-task)** / **~20.741 (-44,6%, 4-task)**; Condition 13.109 → **~5.897 (-55,0%, 3-task)** / **~5.824 (-55,6%, 4-task)**; Disease 13.107 → **~5.897 (-55,0%, 3-task)** / **~5.824 (-55,6%, 4-task)**; Detection 4A 23.791 → **~15.262 (-35,8%)**.
   - Detail operasional lengkap tercantum pada `reports/baseline_experiment_plan.md` Bagian 2E dan Bagian 3.
3. **`Three-Classifier Common Evaluation Subset` (Sanity Check 3 Classifier Inti Saja):**
   - **Kriteria (*verified from existing artifact*):** Irisan `split_species_id == split_condition == split_disease_diagnosis` pada `validation` (**50 baris = 50 gambar unik = 40 `meta_component_id`**, hanya mencakup **11 spesies** & **19 kelas penyakit**; 0 overlap dengan Detection) dan `test` (**41 baris = 41 gambar unik = 31 `meta_component_id`**, hanya mencakup **10 spesies** & **15 kelas penyakit**; **3 gambar / 1 `meta_component_id` overlap dengan `train` Detection**).
   - Subset ini **hanya berlaku sebagai sanity check 3 classifier inti**, **bukan** bukti performa pipeline secara umum, dan **bukan** evaluasi end-to-end bebas leakage bila Detection ikut dipakai.
4. **Keterbatasan Jujur & Rekomendasi Jangka Panjang (*unresolved issue* `UD-05`):**  
   Pada split Stage 6 yang independen per task, jaminan isolasi penuh lintas-task hanya tercapai dengan konsekuensi penyusutan ~11–26% data training (Protokol B). Jika pada tahap berikutnya diinginkan evaluasi pipeline end-to-end tanpa penyusutan data training sebesar itu, solusi yang direkomendasikan — dan **memerlukan persetujuan eksplisit pengguna** — adalah menyusun *unified meta-component split* bersama sebagai artefak terpisah (tidak dibuat pada Stage 7).

---

## 4. Keputusan Arsitektur Model per Task (Rekomendasi)

Seluruh kandidat berikut merupakan **rekomendasi transfer learning** berdasarkan ukuran data, kualitas anotasi, imbalance, kompleksitas model, biaya inferensi, dan kendala hardware (lokal: Windows 11, Python 3.13.9, RAM 16 GB, CPU only; training direncanakan di Google Colab GPU). **Belum ada model yang dilatih atau diuji.**

| Task | Kandidat Baseline Utama | Kandidat Pembanding | Pertimbangan Teknis & Hardware |
| :--- | :--- | :--- | :--- |
| **Task 1: Species ID** | `EfficientNet-B0` | `MobileNetV3-Large` | Transfer learning efisien untuk 68 spesies tunggal; kapasitas fitur tekstur daun lebih kuat pada EfficientNet-B0, sedangkan MobileNetV3-Large menawarkan arsitektur lebih ringan untuk opsi deployment CPU/mobile. |
| **Task 2: Condition** | `MobileNetV3-Small` | `EfficientNet-B0` | Klasifikasi biner berimbalance (1 : 4,40); model ringan mengurangi risiko overfitting *shortcut* latar belakang, dibandingkan dengan EfficientNet-B0 untuk menguji kecukupan kapasitas representasi. |
| **Task 3: Disease/Symptom** | `EfficientNet-B0` | `ResNet50` | Gejala mikro (bercak, klorosis, karat) membutuhkan ekstraksi fitur detail; ResNet50 menjadi pembanding berkapasitas lebih besar untuk mengukur apakah arsitektur lebih dalam meningkatkan Macro F1 secara bermakna dibanding biaya komputasinya. |
| **Task 4: Object Detection** | `YOLOv8n` | `YOLO11n` | Arsitektur deteksi single-stage ringan (*anchor-free*) yang realistis dilatih di Colab GPU untuk 70 kelas atomik terverifikasi; perbandingan YOLOv8n vs YOLO11n mengevaluasi akurasi lokalisasi (mAP) dan kelayakan inferensi CPU lokal. |

---

## 5. Kebijakan *Species-Aware Diagnosis Gating*

1. **Verifikasi Cakupan Spesies vs Penyakit:**
   - Dari **68 spesies tunggal** pada Task 1, hanya **20 spesies tunggal** (+ 1 kategori `Houseplants (Multi-Species)` = **21 kategori spesies**) yang memiliki anotasi penyakit aktif pada Task 3 (dan tepat 21 kategori yang sama pada Task 2).
   - Sebanyak **48 spesies tunggal lainnya** tidak memiliki data diagnosis penyakit aktif: **47 spesies tanaman hias** (`goletplant` / `v3i`) dan **1 spesies perkebunan (`Coffee (Coffea)`)** yang hanya memiliki anotasi lokalisasi daun.
2. **Status 95 Pasangan `(species, disease)`:**  
   Ke-95 pasangan yang ditemukan pada manifest aktif adalah ***observed annotation pairs*** (pasangan yang teramati pada dataset), **bukan *verified pathology rules*** secara biologis. Tidak boleh ada klaim kepatuhan biologis 100%.
3. **Lima Eksperimen Gating yang Wajib Dibandingkan pada Stage 8–9:**
   - **Exp G1:** *Unmasked disease baseline* (tanpa gating spesies).
   - **Exp G2:** *Top-2 species gating*.
   - **Exp G3:** *Top-3 species gating*.
   - **Exp G4:** *Soft species prior* (pembobotan probabilitas penyakit oleh distribusi spesies terkalibrasi tanpa memutus total ke $-\infty$).
   - **Exp G5:** *Low-confidence species fallback* (menonaktifkan gating agresif saat confidence spesies di bawah ambang kalibrasi dan mengaktifkan cek konsistensi / abstain).
4. **Penanganan Seluruh Kandidat Top-$k$ (4 Kondisi Eksplisit):**
   - **All candidates in scope:** Seluruh kandidat spesies dalam Top-$k$ termasuk dalam 21 kategori berlabel penyakit → terapkan *Top-$k$ union / soft prior* dan cek konsistensi.
   - **Some candidates in scope:** Sebagian kandidat dalam cakupan, sebagian di luar cakupan → gunakan *soft weighting* dengan peringatan ketidakpastian cakupan; abstain bila konflik.
   - **All candidates out of scope:** Seluruh kandidat berada di luar 21 kategori patologi → terbitkan status **`OUT_OF_PATHOLOGY_SCOPE`**, **tetap tampilkan identifikasi spesies (jika yakin) dan hasil condition classification (jika tersedia/tervalidasi)**, serta jelaskan bahwa diagnosis penyakit belum didukung data.
   - **Species identification uncertain:** Confidence spesies rendah / entropy tinggi → terbitkan **`SPECIES_UNCERTAIN`**, jangan lakukan *hard masking* agresif, dan gunakan jalur fallback/abstain.

---

## 6. Kebijakan Deteksi Objek dan ROI

1. **Pemisahan Tegas Confidence vs IoU:**
   - **IoU tidak boleh digunakan sebagai inference confidence threshold.** IoU hanya digunakan untuk evaluasi terhadap *ground truth* (mAP@0.50, mAP@0.50:0.95) dan mekanisme *post-processing* seperti NMS.
   - Keputusan deteksi saat inferensi menggunakan **confidence output langsung dari implementasi model YOLO terpilih** (catatan: YOLOv8n dan YOLO11n adalah arsitektur *anchor-free* yang menghasilkan skor kelas secara langsung tanpa kepala *objectness* terpisah yang dikalikan dengan skor kelas).
2. **Kebijakan Baseline Full-Image vs Eksperimen ROI:**
   - **Full-image classification adalah baseline utama** untuk Task 1, Task 2, dan Task 3.
   - **ROI crop adalah eksperimen tambahan.** **Dilarang** mengirim *ROI crop* langsung ke classifier yang hanya dilatih menggunakan *full image* tanpa mengevaluasi *distribution shift*. Jika ROI diuji, training dan evaluasi classifier wajib menggunakan strategi crop yang konsisten.
3. **Distingsi Semantik Deteksi:**
   - Bedakan secara tegas **whole-plant detection** (52 `Plant Species` + 10 `Plant Object`), **leaf detection** (1 `Coffee - Leaf Localization`), dan **symptom-region detection** (7 `Houseplants Symptom`).
   - **Deteksi area gejala tidak sama dengan diagnosis penyebab penyakit.**

---

## 7. Rancangan Deployment & Integrasi (Status: Konseptual)

* Lingkungan lokal pengguna (Windows 11, Python 3.13.9, RAM 16 GB, tanpa NVIDIA GPU) digunakan untuk audit data, pengembangan kode, dan pengujian ringan; training berat direncanakan di Google Colab GPU.
* **FastAPI**, **ONNX**, **TFLite**, **Knowledge Base**, dan integrasi **Flutter (`daunku_app`)** berstatus **rancangan konseptual (Tahap 10–13)** dan **belum diimplementasikan**.
* Tidak ada klaim latensi, ukuran model final, atau performa perangkat mobile sebelum benchmark dilakukan pasca-training.

---

## 8. Unresolved Design Decisions

| ID | Keputusan Belum Terselesaikan | Alasan | Bukti yang Dibutuhkan | Dampak pada Stage 8 |
| :--- | :--- | :--- | :--- | :--- |
| **UD-01** | Multiclass vs Multi-Label pada Task 3 (Disease) | 17.870 gambar berupa single-label folder, sementara 879 gambar `v3i` memuat 6 kombinasi multi-gejala (113 gambar). | Eksperimen komparatif multiclass vs multi-label sigmoid pada **`inner_val`** (bukan `val_cal` atau `val_thresh`). | Baseline awal menggunakan **multiclass** pada label yang memenuhi kriteria; multi-label menjadi eksperimen terpisah di tahap berikutnya jika diperlukan. |
| **UD-02** | Penanganan 37 label kombinasi multi-spesies pada Task 1 | 37/37 label kombinasi tidak memiliki sampel Validation (32 train-only, 5 train+test). | Evaluasi apakah multi-spesies ditangani lewat deteksi objek atau multi-label classification. | Baseline utama Task 1 dibatasi pada 68 kelas single-species yang valid di semua split. |
| **UD-03** | Konsolidasi label sinonim/typo sumber pada Task 3 (`Healty leaf`, `Leaf curll`, `Yelllow Mosaic virus`) | Dipertahankan secara konservatif di Stage 5; mengubahnya memerlukan persetujuan ulang taksonomi. | Audit confusion matrix antar label sinonim pada pilot/baseline Stage 8 & persetujuan pengguna. | Macro F1 awal berpotensi tertekan oleh kebingungan antar label sinonim; wajib dilaporkan transparan. |
| **UD-04** | Status 2 kelas `Yellow Disease` (`provisional`) pada Task 4 | Ketiadaan file `data.yaml` resmi pada dataset sumber. | Verifikasi visual/metadata untuk memastikan makna Class 0 dan Class 1. | Dieksklusikan dari baseline utama deteksi (70 kelas terverifikasi); hanya diuji pada sub-eksperimen terpisah. |
| **UD-05** | Protokol evaluasi pipeline gabungan lintas-task | Split Stage 6 dibuat terpisah per task sehingga terdapat overlap train-vs-val/test antar-task. | Persetujuan pengguna atas penggunaan OOF predictions atau pembuatan *unified split* baru. | Evaluasi gating lintas-task wajib menggunakan *group-aware OOF* agar bebas *cross-task leakage*. |

---

## 9. Revision Notes (Final Integrated Revision)

- **Temuan Review:** Ditemukan *cross-task split overlap* signifikan antar 4 task Stage 6; selisih historis `goletplant` (26.006 vs 26.063) dan `v3i` (2.830 vs 2.773); 6 label multi-gejala (113 gambar) pada Task 3; 48 spesies tanpa penyakit mencakup `Coffee (Coffea)` bukan hanya indoor; serta kebutuhan memisahkan baseline single-species (68) dari 37 kombinasi dan 70 kelas deteksi terverifikasi dari 2 kelas provisional.
- **Perubahan:** Menambahkan Bagian 3 (*Cross-Task Data Leakage Review*) dengan matriks overlap terverifikasi; memisahkan baseline single-species vs kombinasi dan verified vs provisional detection; mengganti penyebutan 95 pasangan menjadi *observed annotation pairs*; menambahkan 5 eksperimen gating dan 4 kondisi Top-$k$; mempertegas *full-image* sebagai baseline utama dan *ROI crop* sebagai eksperimen tambahan; serta menambahkan tabel `Unresolved Design Decisions`.
- **Angka Terverifikasi:** Seluruh angka berasal langsung dari `split_manifest.csv`, `train/validation/test_manifest.csv`, `split_summary.json`, dan `label_mapping.yaml`.
- **Asumsi Belum Terbukti & Risiko Stage 8:** Tercatat secara eksplisit pada Bagian 8 (`UD-01` s.d. `UD-05`) dan pada `reports/stage7_final_consistency_review.md`.
