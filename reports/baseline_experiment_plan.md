# Rencana Eksperimen Baseline Model (Stage 7 — Final Integrated Revision) — DaunKu AI

> **Tanggal Revisi Final:** 25 November 2026  
> **Status:** Rencana Eksperimen Final — Menunggu Persetujuan sebelum Stage 8 (**Belum Ada Training / Belum Ada Notebook**)  
> **Peran:** Senior Machine Learning Engineer & Experimentation Lead  
> **Artefak Acuan Terverifikasi:**  
> - `daunku_ai/reports/model_architecture_recommendation.md`  
> - `daunku_ai/artifacts/splits/split_manifest.csv`, `train_manifest.csv`, `validation_manifest.csv`, `test_manifest.csv`  
> - `daunku_ai/artifacts/splits/split_config.yaml` & `split_summary.json`  
> - `daunku_ai/configs/label_mapping.yaml`

---

## 1. Prinsip Eksperimen, Reproducibility, & Perlindungan Data

Dokumen ini merinci protokol eksperimen baseline untuk 4 task AI DaunKu yang direncanakan dieksekusi pada **Stage 8** menggunakan GPU cloud (Google Colab GPU). **Tidak ada klaim hasil eksperimen, akurasi, latensi, maupun jaminan kebutuhan VRAM yang dibuat pada tahap ini.**

### Aturan Wajib Eksperimen:
1. **Pemisahan Seed:**
   - `SPLIT_SEED = 42` — Mengunci pembagian data Stage 6 pada `split_manifest.csv` (tidak boleh diubah).
   - `EXPERIMENT_SEED = 42` — Mengontrol inisialisasi bobot, *DataLoader shuffling*, dan augmentasi stokastik training (terpisah dari seed split; dapat diuji ulang dengan beberapa seed pada tahap stabilitas).
2. **Kebijakan Data Augmentation:**  
   Augmentasi **hanya diterapkan pada Train Set**. Validation Set, Locked Test Set, dan Natural-Background Holdout **tidak boleh** diaugmentasi (hanya *deterministic resize/letterbox* dan normalisasi). Augmentasi warna ekstrem dihindari pada Task 2 & Task 3 agar tidak merusak sinyal klorosis/nekrosis.
3. **Kebijakan Perlindungan Test Set & Holdout:**
   - **Locked Test Set** (`test_manifest.csv`, 14.748 baris unik) **dilarang keras digunakan** untuk training, hyperparameter tuning, model selection, kalibrasi probabilitas, maupun penentuan threshold. Test set hanya dievaluasi satu kali pada tahap evaluasi resmi (Stage 9).
   - **Natural-Background Holdout** (`natural_background_holdout.csv`, 2.067 baris / 689 foto dasar Marigold alami) **hanya digunakan untuk evaluasi ketahanan (*robustness evaluation*) setelah model dan seluruh threshold dibekukan**.
4. **Kebijakan *Cross-Task Leakage* & Status OOF (`DEFERRED`):**  
   Split Stage 6 dipertahankan sebagai baseline historis untuk eksperimen per-task (*zero known/audited leakage pairs across splits* secara intra-task). **OOF calibration berstatus *deferred*** dan **bukan persyaratan baseline pertama** (belum siap digunakan sampai protokol *nested training* dan *calibration* divalidasi). Kebutuhan *unified split* dapat dievaluasi kembali ketika integrasi multi-model benar-benar diperlukan. **`Three-Classifier Common Evaluation Subset`** (50 Val / 41 Test) hanya digunakan sebagai *sanity check* 3 classifier inti.

---

## 2. Rencana Eksperimen Baseline per Task AI

### A. Task 1: Plant Species Identification
* **Dataset & Split Counts (`split_species_id` — Terverifikasi Langsung dari Manifest):**
  - Total aktif manifest (105 label): **49.630 gambar unik** (Train: **37.500** | Val: **6.068** | Test Locked: **6.062**).
  - **Baseline Utama — 68 Kelas Single-Species (49.523 gambar unik | 25.930 `meta_component_id` unik):**
    - **Train:** **37.408 gambar unik** (**19.447** `meta_component_id` unik; 68 kelas).
    - **Validation:** **6.068 gambar unik** (**3.241** `meta_component_id` unik; 68 kelas).
    - **Test (Locked):** **6.047 gambar unik** (**3.242** `meta_component_id` unik; 68 kelas).
    - **Distribusi per Kelas (68 Single-Species):** Min = **52** (`Dracaena angolensis`: Tr 44 / Val 4 / Te 4), Median = **491,5**, Mean = **728,3**, Max = **5.589** (`Arabian Jasmine`: Tr 4.254 / Val 692 / Te 643). Seluruh 68 kelas hadir lengkap di Train, Validation, dan Test (0 kelas hilang).
  - **Dieksklusikan dari Baseline 68-Class Softmax — 37 Label Kombinasi Multi-Spesies (107 gambar unik | 43 `meta_component_id` unik):**
    - Train: **92 gambar** (37 `meta_component_id`, 37 kelas) | Val: **0 gambar** | Test: **15 gambar** (6 `meta_component_id`, 5 kelas). Tidak dimasukkan ke 68-class softmax; dievaluasi secara terpisah.
    - *Rekonsiliasi:* $49.523 + 107 = 49.630$ gambar unik (tidak ada gambar yang dihitung lebih dari sekali).
* **Candidate Architecture (Rekomendasi):** Baseline utama `EfficientNet-B0`; pembanding `MobileNetV3-Large` (keduanya pretrained ImageNet-1K).
* **Input Size:** $224 \times 224 \times 3$ (full-image classification baseline).
* **Loss Function:** `CrossEntropyLoss(label_smoothing=0.1)` (opsi pembanding: *class-balanced weighting* untuk spesies minoritas seperti `Dracaena angolensis`).
* **Optimizer & Scheduler:** `AdamW` (`weight_decay = 1e-4`), `CosineAnnealingLR` dengan *linear warmup* 3 epoch.
* **Learning Rate:** $\eta_0 = 3 \times 10^{-4}$ (opsi *differential LR*: backbone $1 \times 10^{-4}$, head $1 \times 10^{-3}$).
* **Batch Size Awal (Colab GPU):** 64 *(disesuaikan dengan VRAM aktual via pilot run; gunakan gradient accumulation jika VRAM terbatas)*.
* **Epoch Range & Early Stopping:** 25–30 epoch; *early stopping* `patience = 7` pada `val_macro_f1` (68 kelas tunggal).
* **Class Imbalance Strategy:** Evaluasi *inverse-frequency / effective-number class weights* atau *WeightedRandomSampler* bila recall kelas kecil tertinggal jauh.
* **Data Augmentation (Train Only):** *RandomResizedCrop* (skala konservatif 0,75–1,0), *RandomHorizontalFlip*, rotasi ringan ($\pm 15^\circ$), *ColorJitter* ringan (kecerahan/kontras $\le 0{,}15$).
* **Metrics:** Macro F1-Score (68 spesies tunggal), Top-1 Accuracy, Top-3 Accuracy, Per-class Precision/Recall, ECE.
* **Validation Protocol:** *Early stopping* dan *model selection* menggunakan **`inner_val`** (~15% grup `meta_component_id` dari himpunan training bersih), sehingga Validation Set Stage 6 tetap steril untuk kalibrasi (`val_cal`) dan pemilihan threshold (`val_thresh`).
* **Limitations:** *Background confounding* (pot indoor vs kebun alami); 37 label kombinasi multi-spesies tidak dapat dievaluasi pada Validation Set; 48 dari 68 spesies tunggal tidak memiliki data penyakit aktif di Task 3.
* **Expected Output Artifacts:** `models/task1_<arch>_best.pt`, log metrik per epoch (`reports/training_experiments/task1_*.json`), confusion matrix validation, reliability diagram, dan konfigurasi eksperimen.

---

### B. Task 2: Plant Condition Classification (Healthy vs Unhealthy)
* **Dataset & Split Counts (`split_condition`):**
  - Total aktif: **18.749 gambar** (Train: **13.109** | Val: **2.799** | Test Locked: **2.841**).
  - **Distribusi Aktual (Imbalance 1 : 4,40):**
    - Train: `Healthy` **2.439 (18,61%)** vs `Unhealthy` **10.670 (81,39%)** *(1 : 4,37)*.
    - Validation: `Healthy` **504 (18,01%)** vs `Unhealthy` **2.295 (81,99%)** *(1 : 4,55)*.
    - Test (Locked): `Healthy` **528 (18,59%)** vs `Unhealthy` **2.313 (81,41%)** *(1 : 4,38)*.
  - 0 kelas hilang di split mana pun; 43.667 gambar `Unknown` diisolasi penuh.
* **Candidate Architecture (Rekomendasi):** Baseline utama `MobileNetV3-Small`; pembanding `EfficientNet-B0` (pretrained ImageNet-1K).
* **Input Size:** $224 \times 224 \times 3$ (full-image baseline).
* **Loss Function:** Class-weighted `BCEWithLogitsLoss` (menyesuaikan rasio Train 1 : 4,37, misal `pos_weight` $\approx 4{,}37$ jika kelas positif = `Healthy`, atau $\approx 0{,}23$ jika kelas positif = `Unhealthy`); opsi pembanding *Focal Loss* biner.
* **Optimizer & Scheduler:** `AdamW` (`weight_decay = 1e-4`), `ReduceLROnPlateau(mode='max', factor=0.5, patience=3)` memantau `val_balanced_accuracy`.
* **Learning Rate:** $\eta_0 = 5 \times 10^{-4}$ (`MobileNetV3-Small`) / $3 \times 10^{-4}$ (`EfficientNet-B0`).
* **Batch Size Awal (Colab GPU):** 64 *(disesuaikan dengan VRAM aktual)*.
* **Epoch Range & Early Stopping:** 20–25 epoch; *early stopping* `patience = 8` pada `val_balanced_accuracy`.
* **Class Imbalance Strategy:** Pembobotan loss wajib + pembanding *WeightedRandomSampler* + optimasi threshold keputusan pada Validation Set (bukan mengasumsikan threshold 0,5).
* **Data Augmentation (Train Only):** *RandomHorizontalFlip*, *RandomVerticalFlip* (jika relevan daun), rotasi ringan ($\pm 20^\circ$), *RandomCrop* ringan; **hindari** perubahan hue/saturasi agresif agar warna klorosis tidak berubah.
* **Metrics:** Balanced Accuracy, Macro F1-Score, PR-AUC (kedua kelas), ROC-AUC, Sensitivity (`Unhealthy`), Specificity (`Healthy`), **Subgroup Accuracy per Spesies** (21 kategori), ECE.
* **Validation Protocol:** *Early stopping* dan *model selection* menggunakan **`inner_val`** (~15% grup `meta_component_id` dari himpunan training bersih); Validation Set Stage 6 dipakai khusus untuk `val_cal` (Temperature Scaling) dan `val_thresh` (threshold selection berbasis *trade-off* FP vs FN).
* **Limitations:** Ketimpangan kelas signifikan (1 : 4,40); risiko *shortcut learning* antar dataset sumber; hanya mencakup 21 kategori spesies.
* **Expected Output Artifacts:** `models/task2_<arch>_best.pt`, log metrik, kurva PR/ROC validation, tabel subgroup accuracy per spesies, reliability diagram.

---

### C. Task 3: Disease/Symptom Diagnosis
* **Dataset & Split Counts (`split_disease_diagnosis`):**
  - Total aktif: **18.749 gambar** (Train: **13.107** | Val: **2.788** | Test Locked: **2.854**).
  - **53 label aktif:** **50 label hadir di seluruh split**; **3 label multi-gejala bersifat train-only** (`Dehydration + Leaf Curl`, `Dehydration + Leaf Curl + Over-watering`, `Over-watering + Rust`).
  - **Struktur Anotasi:** 17.870 `classification_folder` + 879 `bbox_tensorflow_csv` (`v3i`, memuat **6 label kombinasi multi-gejala** = 113 gambar).
* **Candidate Architecture (Rekomendasi):** Baseline utama `EfficientNet-B0`; pembanding `ResNet50` (pretrained ImageNet-1K).
* **Input Size:** $224 \times 224 \times 3$ (baseline awal); opsi eksperimen lanjutan $320 \times 320$ atau $384 \times 384$ bila gejala mikro kurang tertangkap.
* **Loss Function:**
  - *Baseline Multiclass:* `FocalLoss(gamma=2.0, alpha=effective_class_weights)` atau *weighted* `CrossEntropyLoss` pada kelas tunggal yang terwakili di seluruh split.
  - *Eksperimen Multi-Label (untuk `UD-01` / subset `v3i`):* `BCEWithLogitsLoss` berbobot pada gejala atomik.
* **Optimizer & Scheduler:** `AdamW` (`weight_decay = 1e-4`), `CosineAnnealingLR` dengan *warmup* 3 epoch.
* **Learning Rate:** $\eta_0 = 2 \times 10^{-4}$.
* **Batch Size Awal (Colab GPU):** 32 *(disesuaikan dengan VRAM aktual; turunkan ke 16 + gradient accumulation 2x untuk ResNet50 atau resolusi tinggi)*.
* **Epoch Range & Early Stopping:** 30–35 epoch; *early stopping* `patience = 10` pada `val_macro_f1`.
* **Class Imbalance Strategy:** Effective-number class weighting / Focal Loss; pelaporan metrik terpisah untuk kelas bervolume kecil (misal `MYMV` Val=2, `bunchy top` Val=2, `Over-watering` Val=3).
* **Data Augmentation (Train Only):** Flip horizontal/vertikal, rotasi ringan, *RandomCrop* konservatif; hindari distorsi warna kuat yang mengubah tanda penyakit.
* **Eksperimen *Species-Aware Gating* (5 Skenario — Tahap Integrasi Multi-Model; OOF Calibration `DEFERRED`):**
  1. **G1:** *Unmasked disease baseline*.
  2. **G2:** *Top-2 species gating* (berbasis *observed annotation pairs* 95 pasangan).
  3. **G3:** *Top-3 species gating*.
  4. **G4:** *Soft species prior*.
  5. **G5:** *Low-confidence species fallback* (tanpa *hard masking* saat confidence spesies rendah).
* **Metrics:** Macro F1-Score (50 kelas terwakili), Weighted F1, Per-Class Precision & Recall, Confusion Matrix, ECE, **Risk-Coverage Curve** (membandingkan G1–G5).
* **Validation Protocol:** *Early stopping* dan *model selection* intra-task menggunakan **`inner_val`** (~15% grup dari training bersih); Validation Set Stage 6 dipakai khusus untuk `val_cal` & `val_thresh`. Untuk evaluasi pipeline gabungan lintas-task, gunakan **Jalur 2 (Protocol B)** pada Bagian 2E.
* **Limitations:** 3 kelas train-only tidak dapat dievaluasi; isu belum terselesaikan (`UD-01` multiclass vs multi-label, `UD-03` fragmentasi label sinonim seperti `Healty leaf` vs `None (Healthy)`); cakupan terbatas pada 21 kategori spesies.
* **Expected Output Artifacts:** `models/task3_<arch>_best.pt`, log eksperimen, tabel perbandingan G1–G5, confusion matrix, reliability diagram, risk-coverage curve.

---

### D. Task 4: Object / Leaf Detection
* **Dataset & Split Counts (`split_leaf_detection`):**
  - Total aktif manifest: **37.070 gambar** (Train: **27.600** | Val: **4.888** | Test Locked: **4.582**).
  - **Sumber Data Terverifikasi:** `goletplant` (**26.006**), `v3i` (**2.830**), `Kopi` (**3.139**), `Yellow Disease` (**5.095**, `provisional`).
  - **Pemisahan Eksperimen Wajib:**
    - **Sub-eksperimen 4A — Baseline Utama (70 Kelas Objek Atomik Terverifikasi, Non-Yellow):** **31.975 gambar** (Train: 23.791 | Val: 4.251 | Test: 3.933) — mencakup 52 `Plant Species` (whole-plant), 10 `Plant Object`, 7 `Houseplants Symptom`, 1 `Coffee - Leaf Localization`. Seluruh 70 kelas atomik hadir di semua split.
    - **Sub-eksperimen 4B — Eksperimen Terpisah (`Yellow Disease`, 2 Kelas Provisional):** **5.095 gambar** (Train: 3.809 | Val: 637 | Test: 649). Tidak digabung ke klaim baseline utama sebelum verifikasi metadata selesai.
* **Candidate Architecture (Rekomendasi):** Baseline utama `YOLOv8n`; pembanding `YOLO11n` (pretrained COCO; keduanya *anchor-free* dengan output per-class confidence langsung tanpa *objectness head* terpisah).
* **Input Size:** $640 \times 640 \times 3$.
* **Loss Function:** Gabungan CIoU Loss (regresi boks), DFL (*Distribution Focal Loss*), dan BCE Classification Loss sesuai implementasi resmi framework YOLO.
* **Optimizer & Scheduler:** `AdamW` atau `SGD` (momentum 0,937) dengan *linear/cosine LR decay* dan warmup 3 epoch.
* **Learning Rate:** $\eta_0 = 1 \times 10^{-3}$ (`AdamW`) atau $1 \times 10^{-2}$ (`SGD`).
* **Batch Size Awal (Colab GPU):** 32 *(disesuaikan dengan VRAM aktual; turunkan ke 16 bila diperlukan)*.
* **Epoch Range & Early Stopping:** 40–50 epoch; *early stopping* `patience = 10` pada `val_mAP@0.50:0.95`.
* **Class Imbalance Strategy:** Pelaporan AP per kategori semantik (whole-plant vs leaf kopi vs gejala `v3i` yang berfrekuensi rendah).
* **Data Augmentation (Train Only):** Mosaic (dinonaktifkan pada 10 epoch terakhir), flip horizontal, skala/translasi ringan; hindari distorsi HSV ekstrem untuk kelas gejala `v3i`.
* **Metrics:** mAP@0.50 (IoU $\ge 0{,}50$ terhadap *ground truth*), mAP@0.50:0.95, Precision, Recall, AP per kelas atomik, analisis boks *false positive* / *missed detection*.
* **Validation Protocol:** *Early stopping* dan *model selection* menggunakan **`inner_val`** (~15% grup dari training bersih); Validation Set Stage 6 dipakai khusus untuk pemilihan `det_conf` pada `val_thresh` (berdasarkan kurva Precision–Recall); **IoU** hanya untuk evaluasi *ground truth* dan NMS.
* **Eksperimen ROI Crop Tambahan (Opsional, Setelah Baseline Full-Image):**  
  Jika ROI crop diuji untuk klasifikasi, classifier **wajib dilatih dan dievaluasi menggunakan strategi crop yang konsisten** (tidak mengirim ROI crop ke classifier yang hanya dilatih pada *full image* tanpa evaluasi *distribution shift*).
* **Limitations:** Heterogenitas semantik anotasi (whole-plant vs daun vs gejala); tidak mencakup Tomat, Kentang, Melati, Mawar, Karet, Kembang Sepatu; deteksi area gejala bukan diagnosis penyebab penyakit.
* **Expected Output Artifacts:** `models/task4_<arch>_best.pt`, kurva PR & mAP per kelas, contoh visual prediksi benar/salah pada Validation Set.

---

### E. Protokol Lintas-Task: Pemisahan OOF Training vs Eksklusi Penuh Evaluasi (*Proposed Protocol*)

**Temuan Metodologis Kritis:** OOF 5-fold standar yang hanya mengecualikan *fold saat ini* **tidak menjamin** seluruh Locked Test Set bebas dari paparan training (karena model fold-$j$ tetap dilatih pada kelompok test milik fold lain $k \neq j$). Oleh karena itu, protokol lintas-task dipisahkan menjadi **dua protokol terpisah** yang berlaku untuk seluruh model dalam pipeline (**Species Identification**, **Condition Classification**, **Disease/Symptom Diagnosis**, serta **Object/Leaf Detection** bila digunakan dalam pipeline atau ROI experiment). Split Stage 6 tidak diubah.

#### Protokol A — Group-Aware OOF & OOF Calibration (`DEFERRED` — Bukan Persyaratan Baseline Pertama)
- **Status:** **`DEFERRED`** — OOF calibration **tidak dijadikan persyaratan baseline pertama** dan **belum siap digunakan** sampai protokol *nested training* dan *calibration* divalidasi.
- **Tujuan (Bila Diaktifkan Nanti):** Menghasilkan *training features* atau prediksi *cross-fitted* yang aman untuk melatih komponen downstream/gating/stacking.
- **Konfigurasi Fold:** `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` (`OOF_SEED = 42`) dengan `groups = meta_component_id`, diterapkan **hanya pada himpunan training bersih setelah mengeksklusikan seluruh himpunan evaluasi pada Protokol B**.
- **Aturan Wajib:** Seluruh gambar dalam satu `meta_component_id` berada pada fold yang sama (`assert` 0 overlap antar fold). Setiap prediksi OOF untuk fold-$j$ dihasilkan oleh model $M^{(j)}$ (dan calibrator $T^{(j)}$ yang di-fit pada inner-cal di luar fold-$j$) yang **tidak pernah dilatih pada `meta_component_id` yang sedang diprediksi**.

#### Protokol B — Pemisahan Ketat `inner_val` vs `val_cal` vs `val_thresh` vs `E_test` (*Proposed Protocol*)
- **1. Pemisahan Dua Jalur Model (Menghilangkan Konflik Penggunaan Validation Set):**
  - **Jalur 1 — Model Baseline Per-Task (Intra-Task):** Melatih tiap task pada split Stage 6 masing-masing, dengan menyisihkan **~15% `inner_val`** (group-aware berdasarkan `meta_component_id`) dari `train` Stage 6 khusus untuk *early stopping* dan *model selection*. Validation Set Stage 6 tetap steril untuk `val_cal` dan `val_thresh`.
  - **Jalur 2 — Model Evaluasi Pipeline Gabungan (Cross-Task Protocol B):** Mengeksklusikan seluruh `E_val ∪ E_test` terlebih dahulu untuk membentuk *clean training pool*, lalu memisahkan **~15% `inner_val`** dari *clean training pool* tersebut khusus untuk *early stopping*, *model selection*, dan *hyperparameter tuning*.
- **2. Definisi Seragam `E_test`, `E_val`, dan `E_val_clean` (*derived calculation* dari `split_manifest.csv`):**
  - **`E_test`:** Gabungan `meta_component_id` Locked Test lintas-task yang terlibat ($E_{\text{test},3}$ = **6.841 mc** untuk 3 task klasifikasi; $E_{\text{test},4}$ = **8.343 mc** untuk 4 task).
  - **`E_val`:** Gabungan `meta_component_id` Validation Set lintas-task yang terlibat ($E_{\text{val},3}$ = **6.783 mc**; $E_{\text{val},4}$ = **8.241 mc**).
  - **`E_val_clean`:** `E_val` setelah mengeluarkan seluruh grup yang overlap dengan `E_test` ($E_{\text{val},3}^{\text{clean}} = E_{\text{val},3} \setminus E_{\text{test},3}$ = **5.250 mc**; $E_{\text{val},4}^{\text{clean}} = E_{\text{val},4} \setminus E_{\text{test},4}$ = **6.302 mc**).
  - **`val_cal` & `val_thresh`:** Partisi terencana dari `E_val_clean` (*proposed protocol*, **bukan** artefak Stage 6).
- **3. Aturan Isolasi Ketat 4 Peran Data:**
  - **`inner_val`:** Khusus untuk *early stopping*, *model selection*, dan *hyperparameter tuning*.
  - **`val_cal`:** Khusus untuk fitting **Temperature Scaling**.
  - **`val_thresh`:** Khusus untuk **threshold selection** (dan metrik tuning ECE/Reliability Diagram).
  - **`E_test`:** Terkunci sepenuhnya — tidak pernah digunakan untuk training, `inner_val`, early stopping, model selection, hyperparameter tuning, calibration, maupun threshold selection.
  - **Jaminan Base Model:** Base model yang menghasilkan prediksi `val_cal`, `val_thresh`, dan `E_test` **tidak boleh pernah** menggunakan grup dari `val_cal`, `val_thresh`, maupun `E_test` untuk training, early stopping, model selection, atau hyperparameter tuning.
- **4. Evaluasi Total Dampak Penyusutan Training Termasuk 15% `inner_val` (*derived calculation* dari `split_manifest.csv`):**

| Task (Total Train Stage 6) | Jalur 1 Intra-Task: ~85% `inner_train` (dari Train Stage 6) | Clean Training Pool (Train Stage 6 di luar `E_val ∪ E_test`, 3-task / 4-task) | Jalur 2 Total Protocol B + 15% `inner_val`: ~85% `inner_train` (dari Clean Pool, 3-task / 4-task)* |
| :--- | :---: | :---: | :---: |
| `Species ID` (68 single-species: 37.408) | ~31.797 (-15,0%) | 30.265 / 24.401 | **~25.725 (-31,2%)** / **~20.741 (-44,6%)** |
| `Species ID` (semua 105: 37.500) | ~31.875 (-15,0%) | 30.357 / 24.490 | **~25.803 (-31,2%)** / **~20.816 (-44,5%)** |
| `Condition` (13.109) | ~11.143 (-15,0%) | 6.938 / 6.852 | **~5.897 (-55,0%)** / **~5.824 (-55,6%)** |
| `Disease Diagnosis` (13.107) | ~11.141 (-15,0%) | 6.938 / 6.852 | **~5.897 (-55,0%)** / **~5.824 (-55,6%)** |
| `Detection 4A` (70 verified: 23.791) | ~20.222 (-15,0%) | 17.955 / 17.955 | **~15.262 (-35,8%)** / **~15.262 (-35,8%)** |
| `Detection` (semua: 27.600) | ~23.460 (-15,0%) | 21.764 / 21.764 | **~18.499 (-33,0%)** / **~18.499 (-33,0%)** |

*\*Catatan: Angka `~85% inner_train` di atas adalah estimasi proporsional turunan (85% dari exact clean pool). Jumlah gambar aktual pasca-pemartisian group-aware `meta_component_id` dapat bergeser ringan ($\pm 1\%$) dan dicatat eksak saat pilot run Stage 8.*
- **5. Keterbatasan Jujur & Keputusan Pengguna (`UD-05`):**  
  Dengan pemisahan penuh `inner_val` + eksklusi `E_val ∪ E_test` pada split Stage 6 independen saat ini, **Condition dan Disease kehilangan ~55,0%–55,6% data training asli** dan **Species 68-cls kehilangan hingga ~44,6%**. Oleh karena itu, pilihan antara menjalankan Jalur 2 Protocol B pada split saat ini versus menyusun *unified meta-component split* bersama sebagai artefak baru terpisah berstatus **`Requires user decision` (`UD-05`)**.

---

## 3. Protokol Kalibrasi & Pemilihan Threshold (`val_cal` vs `val_thresh` — *Proposed Protocol*)

> [!NOTE]
> **`val_cal` dan `val_thresh` adalah partisi terencana dari `E_val_clean` (*proposed protocol*), BUKAN artefak split Stage 6 yang sudah dibuat.**

1. **Konsistensi Grup Lintas-Task:** Pembagian dilakukan satu kali pada level **`meta_component_id`** dari `E_val_clean` (`CALIBRATION_SPLIT_SEED = 42`).
2. **Status Metode Stratifikasi (Jujur):**
   - **Jalur 1 Intra-Task (1 task berdiri sendiri, 1 target label):** Menggunakan `StratifiedGroupKFold(n_splits=2, shuffle=True, random_state=42)` pada label utama task tersebut.
   - **Jalur 2 Lintas-Task (`E_val_clean` dengan label berbeda antar task):** **Metode stratifikasi multi-task formal BELUM dirancang (`Unresolved`).** `StratifiedGroupKFold` **tidak diklaim** menyelesaikan stratifikasi lintas-task karena target stratifikasi multi-task belum didefinisikan. Penyelesaian metode ini diperlukan sebelum eksekusi Jalur 2 Stage 8.
3. **Penetapan Fold Deterministik:** **Fold 0 = `val_cal`** (hanya Temperature Scaling); **Fold 1 = `val_thresh`** (hanya threshold selection & metrik tuning ECE/Reliability Diagram/Risk-Coverage).
4. **Perlindungan Base Model & `E_test`:** Base model yang memprediksi `val_cal`, `val_thresh`, dan `E_test` tidak pernah menggunakan grup dari `val_cal`, `val_thresh`, maupun `E_test` untuk training, early stopping, model selection, atau hyperparameter tuning. Wajib lulus `assert len(set(val_cal.mc) & set(val_thresh.mc)) == 0` dan `assert len((set(val_cal.mc) | set(val_thresh.mc)) & E_test) == 0`.
5. **Keterbatasan Kelas Langka & Holdout:** Pada Validation Set Stage 6, Task 3 memiliki 2 kelas dengan 1 `meta_component_id` (`Dehydration + Over-watering` & `Over-watering`) yang tidak dapat dipecah antar fold. Metrik pada `val_thresh` adalah bagian tuning (bukan estimasi final tak-bias). `E_test` tetap terkunci total; **Natural-Background Holdout** (2.067 baris / 689 foto dasar Marigold) hanya dipakai untuk *robustness evaluation* pasca-pembekuan.

---

## 4. Matriks Rekapitulasi Rencana Eksperimen Baseline

| Parameter | Task 1: Species ID | Task 2: Condition | Task 3: Disease/Symptom | Task 4: Detection (Baseline 4A) |
| :--- | :---: | :---: | :---: | :---: |
| **Seed Split / Seed Exp** | `SPLIT=42` / `EXP=42` | `SPLIT=42` / `EXP=42` | `SPLIT=42` / `EXP=42` | `SPLIT=42` / `EXP=42` |
| **Data Aktif (Tr/Val/Te)** | 37.408 / 6.068 / 6.047 *(68-cls; +107 komb.)* | 13.109 / 2.799 / 2.841 | 13.107 / 2.788 / 2.854 | 23.791 / 4.251 / 3.933 *(+5.095 4B)* |
| **Cakupan Kelas Baseline** | 68 single-species *(37 komb. terpisah)* | 2 kelas *(18,51% vs 81,49%)* | 50 kelas di semua split *(3 train-only)* | 70 atomik terverifikasi *(2 prov. terpisah)* |
| **Model Baseline** | `EfficientNet-B0` | `MobileNetV3-Small` | `EfficientNet-B0` | `YOLOv8n` |
| **Model Pembanding** | `MobileNetV3-Large` | `EfficientNet-B0` | `ResNet50` | `YOLO11n` |
| **Input Size** | $224 \times 224$ | $224 \times 224$ | $224 \times 224$ *(opsi 320/384)* | $640 \times 640$ |
| **Loss Function** | CE (Label Smooth 0,1) | Weighted BCEWithLogits | Focal / Weighted CE *(+ML exp)* | CIoU + DFL + BCE |
| **Optimizer & LR Awal** | AdamW, $3 \times 10^{-4}$ | AdamW, $5 \times 10^{-4}$ / $3 \times 10^{-4}$ | AdamW, $2 \times 10^{-4}$ | AdamW $10^{-3}$ / SGD $10^{-2}$ |
| **Scheduler** | Cosine + Warmup 3 | ReduceLROnPlateau | Cosine + Warmup 3 | Linear / Cosine Decay |
| **Batch Size Awal*** | 64 | 64 | 32 | 32 |
| **Epoch Range & ES** | 25–30 (`val_macro_f1`, p=7) | 20–25 (`val_bal_acc`, p=8) | 30–35 (`val_macro_f1`, p=10) | 40–50 (`val_mAP50-95`, p=10) |
| **Metrik Kunci** | Macro F1 (68), Top-1/3, ECE | Bal. Acc, Macro F1, PR-AUC | Macro F1 (50), G1–G5, ECE | mAP@0.50, mAP@0.50:0.95, AP |

*\*Batch size awal disesuaikan berdasarkan kapasitas VRAM aktual saat pilot run di Colab GPU; tidak ada jaminan kebutuhan VRAM.*

---

## 5. Revision Notes (Final Integrated Revision)

- **Temuan Review:** Perlu pemisahan tegas antara baseline single-species (68) vs 37 kombinasi, pemisahan baseline deteksi 70 kelas terverifikasi (31.975 gambar) vs 2 kelas `Yellow Disease` provisional (5.095 gambar), penyebutan 5 skenario gating (G1–G5) dengan evaluasi *group-aware OOF* untuk mencegah *cross-task leakage*, koreksi bahwa YOLOv8n/YOLO11n tidak memiliki *objectness head* terpisah, serta protokol pemisahan *group-aware* Validation Set (`val_cal` vs `val_thresh`) untuk kalibrasi & pemilihan threshold.
- **Perubahan:** Memperbarui seluruh spesifikasi Task 1–4, menambahkan Bagian 3 (*Group-Aware Calibration & Threshold Selection*), memperjelas kebijakan *Natural-Background Holdout* hanya untuk evaluasi ketahanan pasca-pembekuan, serta menyelaraskan seluruh angka dan penamaan model (`YOLO11n`) dengan dokumen arsitektur dan diagram pipeline.
- **Angka Terverifikasi:** Identik 100% dengan `model_architecture_recommendation.md` dan `stage7_final_consistency_review.md`.
- **Risiko Stage 8:** *Cross-task leakage* pada evaluasi pipeline gabungan (dimitigasi via OOF), fragmentasi label sinonim Task 3, kelas sangat kecil pada Validation, dan variasi VRAM GPU Colab aktual.
