# Stage 7 Final Consistency Review — DaunKu AI

> **Tanggal Audit Konsistensi:** 26 November 2026 (Final Stage 7 Closeout)  
> **Peran:** Senior Machine Learning Engineer, AI Architect, & Data Auditor  
> **Status:** **`STAGE 7 COMPLETE`** — Memenuhi seluruh kriteria closeout baseline (**STOP sebelum Stage 8; menunggu persetujuan eksplisit pengguna**)

---

## 1. File yang Diperiksa & Artefak Sumber yang Digunakan

### A. Dokumen Stage 7 yang Direvisi & Diaudit (3 Dokumen)
1. `daunku_ai/reports/model_architecture_recommendation.md`
2. `daunku_ai/reports/baseline_experiment_plan.md`
3. `daunku_ai/reports/model_pipeline_diagram.md`

### B. Artefak Sumber Kebenaran yang Digunakan (Read-Only, Tidak Dimodifikasi)
- `daunku_ai/artifacts/splits/split_manifest.csv` (85.022 baris)
- `daunku_ai/artifacts/splits/train_manifest.csv` (51.120 baris)
- `daunku_ai/artifacts/splits/validation_manifest.csv` (14.850 baris)
- `daunku_ai/artifacts/splits/test_manifest.csv` (14.748 baris)
- `daunku_ai/artifacts/splits/split_config.yaml` & `split_summary.json`
- `daunku_ai/artifacts/canonical_manifest.csv` (85.022 baris)
- `daunku_ai/configs/label_mapping.yaml` (337 entri label)
- `daunku_ai/reports/canonical_dataset_design.md`
- `daunku_ai/reports/stage5_final_validation.md`
- `daunku_ai/reports/stage6_1_final_integrity_review.md` *(catatan: file aktual bernama `stage6_1_final_integrity_review.md`, bukan `stage6_1_final_review.md`)*
- `daunku_ai/reports/environment_audit.md`
- `daunku_ai/Rencana_Implementasi_AI_DaunKu.md`

---

## 2. Angka yang Berhasil Diverifikasi (100% Berbasis Artefak Aktual)

| Kategori | Metrik / Rincian | Angka Terverifikasi | Sumber Verifikasi |
| :--- | :--- | :--- | :--- |
| **Manifest Global** | Total baris unik / `train_manifest` / `val_manifest` / `test_manifest` | **85.022** / **51.120** / **14.850** / **14.748** | `split_manifest.csv` & 3 file split |
| **Holdout & Quarantine** | `natural_background_holdout` / `quarantined` | **2.067** (689 foto dasar) / **1.266** | `split_manifest.csv`, `stage5_final_validation.md` |
| **Task 1: Species ID (Total 105)** | Train / Val / Test (Total Aktif) | **37.500** / **6.068** / **6.062** (**49.630** gambar unik) | `split_manifest.csv`, `split_summary.json` |
| **Task 1: Baseline 68 Single-Species** | Train / Val / Test (Total & `meta_component_id`) | **37.408** (19.447 mc) / **6.068** (3.241 mc) / **6.047** (3.242 mc) = **49.523 gambar unik** (**25.930** mc; Min 52 `Dracaena angolensis`, Median 491,5, Max 5.589 `Arabian Jasmine`) | `split_manifest.csv` |
| **Task 1: Excluded 37 Multi-Species** | Train / Val / Test (Total & `meta_component_id`) | **92** (37 mc) / **0** (0 mc) / **15** (6 mc) = **107 gambar unik** (43 mc; 8 mc berbagi grup dengan single-species; $49.523 + 107 = 49.630$) | `split_manifest.csv` |
| **Task 2: Condition** | Train / Val / Test (Total Aktif) | **13.109** / **2.799** / **2.841** (**18.749**) | `split_manifest.csv`, `split_summary.json` |
| **Task 2: Imbalance** | `Healthy` vs `Unhealthy` (Total Aktif) | **3.471 (18,51%)** vs **15.278 (81,49%)** — rasio **1 : 4,40** | `split_manifest.csv` |
| **Task 2: Per Split** | Train / Val / Test (`Healthy` : `Unhealthy`) | Tr **2.439:10.670** \| Val **504:2.295** \| Te **528:2.313** | `split_manifest.csv` |
| **Task 3: Disease** | Train / Val / Test (Total Aktif) | **13.107** / **2.788** / **2.854** (**18.749**) | `split_manifest.csv`, `split_summary.json` |
| **Task 3: Kelas** | Total aktif / Semua split / Train-only / Multi-gejala | **53** / **50** / **3** / **6 label (113 gambar `v3i`)** | `split_manifest.csv` |
| **Task 3: Cakupan** | Kategori spesies aktif / Observed `(species, disease)` pairs | **21 kategori** (20 tunggal + `Houseplants Multi-Species`) / **95 pasangan** | `split_manifest.csv` |
| **Spesies Non-Disease** | Spesies tunggal tanpa anotasi penyakit aktif | **48 spesies** (47 tanaman hias `goletplant`/`v3i` + 1 `Coffee (Coffea)`) | `split_manifest.csv` |
| **Task 4: Detection** | Train / Val / Test (Total Aktif) | **27.600** / **4.888** / **4.582** (**37.070**) | `split_manifest.csv`, `split_summary.json` |
| **Task 4: Sumber** | `goletplant` / `Yellow Disease` / `Kopi` / `v3i` | **26.006** / **5.095** (`provisional`) / **3.139** / **2.830** | `split_manifest.csv` |
| **Task 4: Kelas** | Atomik terverifikasi / Atomik provisional / Kombinasi gambar | **70** (31.975 gambar) / **2** (5.095 gambar) / **154** (67 tanpa Val, 53 tanpa Test) | `split_manifest.csv` |

---

## 3. Rekonsiliasi Detection Classes & Perbedaan yang Diselesaikan

### A. Tabel Rekonsiliasi Detection Classes (*verified from manifest*)

| Definisi Kelas Detection | Jumlah Kelas | Distribusi Split (Tr / Val / Te) | Kelas Hilang per Split | Sumber Verifikasi | Status Verifikasi |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Image-level label combinations** (`canonical_label` / `original_label`) | **154** *(151 `included` + 3 `Yellow`)* | **153 / 87 / 101** | 1 hilang di Train; 67 hilang di Val; 53 hilang di Test | `split_manifest.csv`, `split_summary.json`, `label_mapping.yaml` | **Verified from manifest** |
| **Atomic bbox classes (all 4 sources)** | **72** | **72 / 72 / 72** | **0** | `split_manifest.csv` | **Verified from manifest** |
| **Atomic bbox verified (Non-Yellow — Baseline 4A)** | **70** *(52 Species + 10 Object + 7 Symptom + 1 Coffee Leaf)* | **70 / 70 / 70** | **0** (min mc: Tr=15, Val=3, Te=2) | `split_manifest.csv` (31.975 img) | **Verified from manifest** |
| **Atomic bbox `Yellow Disease` provisional (4B)** | **2** (`Class 0`, `Class 1`) | **2 / 2 / 2** | **0** (0 overlap dgn 70 kelas) | `split_manifest.csv` (5.095 img) | **Verified provisional (`pending_review`)** |
| **Teks Stage 6.1 (`149 kelas`, `50 rare`)** | **149** *(legacy textual claim)* / **50** *(rare)* | `149` tidak dihitung di `audit_stage6_1_integrity.py` | `50` cocok dgn `rare_classes` di `split_summary.json`; **`149` adalah `legacy textual claim` yang belum dapat direkonsiliasi** terhadap 154/151/72/70 | `stage6_1_final_integrity_review.md` | **Unresolved legacy textual claim** *(tidak diubah otomatis)* |

### B. Verifikasi Sumber Task 3 & Baseline 68 Single-Species (*verified from manifest*)
1. **Task 3 (`17.870 + 879 = 18.749`):** `classification_folder` (**17.870** baris = `image_id` = `relative_path`; 14.360 `meta_component_id`) dan `bbox_tensorflow_csv` (**879** baris = `image_id` = `relative_path`; 333 `meta_component_id`) terbukti memiliki **0 overlap** pada `image_id`, `relative_path`, `parent_source_group_id`, maupun `meta_component_id`. Total **18.749 gambar unik** (14.693 `meta_component_id`).
2. **Baseline 68 Single-Species (`49.523`):** Terbukti sebagai **49.523 baris = 49.523 `image_id` unik = 49.523 `relative_path` unik** (Tr 37.408 / Val 6.068 / Te 6.047; **25.930 `meta_component_id` unik**). Catatan kehati-hatian: `Dracaena angolensis` hanya memiliki **2 `meta_component_id` (4 gambar)** pada Validation dan Test sehingga evaluasi per kelasnya bervarians tinggi. **8 `meta_component_id`** yang berbagi antara 68 single-species dan 37 kombinasi seluruhnya berasal dari `goletplant` (6 di `train`, 2 di `test`, 0 lintas-split).
3. **Perbedaan Lain yang Diselesaikan:** `goletplant` (**26.006** aktif) & `v3i` (**2.830** aktif); Condition imbalance (**18,51% vs 81,49%**); 48 spesies non-disease (47 tanaman hias + 1 `Coffee`); 95 *observed annotation pairs*; pemisahan **6 Terminal `result_state`** (`INVALID_INPUT` berhenti di validasi, tidak ke KB) vs **Metadata `detection_state`** (`DETECTION_SUCCEEDED`, `DETECTION_NOT_AVAILABLE`, `DETECTION_SKIPPED`); full-image baseline berjalan 1x; dan label ilustratif pada contoh Tomato/Early Blight (204 gambar teramati di manifest, namun JSON hanya contoh format).

---

## 4. Keputusan Arsitektur Final

1. **Arsitektur Modular Multi-Task (`DaunKu HIDS`):** Memisahkan Task 1 (Species), Task 2 (Condition), Task 3 (Disease/Symptom), dan Task 4 (Detection) sebagai model independen yang direkomendasikan (`EfficientNet-B0`, `MobileNetV3-Small`, `MobileNetV3-Large`, `ResNet50`, `YOLOv8n`, `YOLO11n` — seluruhnya masih rekomendasi, belum dilatih).
2. **Baseline Utama = Full-Image Classification:** ROI crop ditetapkan sebagai eksperimen tambahan dengan syarat training/evaluasi crop yang konsisten (mencegah *distribution shift*).
3. **Pemisahan Baseline Single-Species (68) & Detection Terverifikasi (70):** 37 label kombinasi multi-spesies dan 2 kelas `Yellow Disease` (`provisional`) dipisahkan dari baseline utama.
4. **Species-Aware Gating Berbasis Eksperimen (G1–G5):** Membandingkan *Unmasked*, *Top-2*, *Top-3*, *Soft Prior*, dan *Low-Confidence Fallback*, dengan evaluasi seluruh kandidat Top-$k$ (4 kondisi cakupan) serta tetap mempertahankan hasil *Species* dan *Condition* saat *Disease* berstatus `OUT_OF_PATHOLOGY_SCOPE`.
5. **Kalibrasi & Uncertainty Terpisah:** Memisahkan confidence, predictive entropy, dan Top-1/Top-2 margin; penentuan dilakukan melalui *group-aware split* pada Validation Set (`val_cal` vs `val_thresh`) tanpa menyentuh Locked Test Set; *Natural-Background Holdout* hanya untuk *robustness evaluation* pasca-pembekuan.

---

## 5. Cross-Task Leakage Assessment

- **Intra-Task:** Masing-masing dari 4 task memiliki **zero known/audited leakage pairs across splits** di dalam task-nya sendiri.
- **Cross-Task (TEMUAN KRITIS):** Karena Stage 6 membuat split secara terpisah per task, terdapat tumpang tindih signifikan antar task:
  - `Species ID` (`train`) vs `Disease` (`val`/`test`): **4.173 gambar** (1.648 `meta_component` val; 1.626 test).
  - `Species ID` (`train`) vs `Condition` (`val`/`test`): **4.189 gambar** (1.629 val; 1.640 test).
  - `Condition` (`train`) vs `Disease` (`val`/`test`): **3.964 gambar** (1.533 val; 1.557 test).
  - `Species ID` (`train`) vs `Detection` (`val`/`test`): **5.936 gambar** (1.002 val; 1.078 test).
- **Cross-Task `test`-in-one-task vs `val`-in-another-task (*verified from manifest*):** `Species test` vs `Disease val` = **256 mc (312 img)**; `Species test` vs `Condition val` = **289 mc (351 img)**; `Condition test` vs `Disease val` = **330 mc (420 img)**; `Disease test` vs `Species val` = **300 mc (382 img)**; `Detection test` vs `Species val` = **178 mc (475 img)**.
- **`Three-Classifier Common Evaluation Subset` (Irisan 3 Classifier Inti Saja):** **50 gambar Validation** (40 mc; hanya 11 spesies & 19 penyakit; 0 overlap Detection) dan **41 gambar Test** (31 mc; hanya 10 spesies & 15 penyakit; **3 gambar / 1 mc overlap dengan `train` Detection**). Hanya berlaku sebagai *sanity check* 3 classifier inti, **bukan** bukti performa pipeline umum dan **bukan** evaluasi end-to-end bebas leakage bila Detection ikut digunakan.
- **Mitigasi Non-Destruktif (*Proposed Protocol*, Tanpa Mengubah Split Stage 6):** Dipisahkan menjadi **Jalur 1 (Intra-Task)** dan **Jalur 2 (Pipeline Gabungan — Protokol A & B)** untuk **Species, Condition, Disease, dan Detection** (bila dipakai):
  - **`inner_val`** (~15% grup dari *clean training pool*): khusus *early stopping*, *model selection*, dan *hyperparameter tuning*.
  - **`E_val`** = gabungan `meta_component_id` Validation lintas-task (**6.783 mc** 3-task / **8.241 mc** 4-task); **`E_val_clean`** = `E_val \ E_test` (**5.250 mc** 3-task / **6.302 mc** 4-task); **`val_cal`** (Fold 0, khusus Temperature Scaling) dan **`val_thresh`** (Fold 1, khusus threshold selection) adalah partisi terencana dari `E_val_clean` (**bukan** artefak Stage 6).
  - **`E_test`** (**6.841 mc** 3-task / **8.343 mc** 4-task): terkunci penuh. Base model yang memprediksi `val_cal`, `val_thresh`, dan `E_test` tidak pernah memakai grup tersebut untuk training, early stopping, model selection, maupun tuning.
  - Metode stratifikasi multi-task pada `E_val_clean` lintas label berbeda berstatus **`Unresolved`** (`StratifiedGroupKFold` hanya berlaku pada mode single-task).
- **Total Dampak Penyusutan Training Termasuk 15% `inner_val` (*Derived Proportional Estimate* dari *Clean Pool* `split_manifest.csv`):**
  - *Jalur 1 Intra-Task (~85% train Stage 6):* Species 68-cls 37.408 → **~31.797 (-15,0%)**; Condition 13.109 → **~11.143 (-15,0%)**; Disease 13.107 → **~11.141 (-15,0%)**; Detection 4A 23.791 → **~20.222 (-15,0%)**.
  - *Jalur 2 Protocol B (`E_val ∪ E_test` + 15% `inner_val`):* Species 68-cls → **~25.725 (-31,2%, 3-task)** / **~20.741 (-44,6%, 4-task)**; Condition → **~5.897 (-55,0%, 3-task)** / **~5.824 (-55,6%, 4-task)**; Disease → **~5.897 (-55,0%, 3-task)** / **~5.824 (-55,6%, 4-task)**; Detection 4A → **~15.262 (-35,8%)**.
  - Tidak diklaim *100% leakage-free* sebelum protokol diimplementasikan dan diaudit pada Stage 8. Solusi jangka panjang tanpa penyusutan data latih sebesar itu (`UD-05`) berstatus **`Requires user decision`**.

---

## 6. Pelacakan Status Masalah (`Resolved` / `Unresolved` / `Pending evidence` / `Requires user decision`)

| ID / Masalah | Status | Ringkasan & Alasan |
| :--- | :---: | :--- |
| **Pemisahan `inner_val`, `val_cal`, `val_thresh`, & `E_test` (Jalur 1 vs Jalur 2)** | **Resolved** | Konflik penggunaan Validation Set diselesaikan: `inner_val` untuk early stopping/model selection, `val_cal` hanya Temperature Scaling, `val_thresh` hanya threshold selection, `E_test` terkunci penuh. |
| **Definisi Seragam `E_val`, `E_val_clean`, & Total Shrinkage (+ 15% `inner_val`)** | **Resolved** | `E_val`, `E_val_clean`, serta total penyusutan training (+ 15% `inner_val`: hingga -55,6% pada Condition/Disease) telah dirumuskan dan dihitung konsisten di semua dokumen. |
| **Konsistensi Tanggal Revisi, 6 Terminal `result_state` + `detection_state`, & Cakupan OOF 4 Task** | **Resolved** | Seluruh 4 dokumen seragam tanggal **25 November 2026**, OOF mencakup Species/Condition/Disease/Detection, dan 6 terminal `result_state` terpisah tegas dari metadata `detection_state`. |
| **Metode Stratifikasi Multi-Task untuk Partisi `E_val_clean`** | **Unresolved** | Desain metodologis stratifikasi lintas task berlabel berbeda (species, condition, disease, bbox) belum selesai; `StratifiedGroupKFold` hanya untuk mode single-task. |
| **Discrepancy `149` Kelas Detection pada Laporan Stage 6.1** | **Unresolved** | Dipertahankan sebagai *legacy textual claim* yang belum dapat direkonsiliasi terhadap 154/151/72/70; laporan Stage 6.1 tidak diubah. |
| **`UD-02` — Penanganan 37 Label Kombinasi Multi-Spesies (Task 1)** | **Unresolved** | 37/37 tidak memiliki sampel Validation (baseline utama dibatasi ke 68 single-species: 49.523 gambar). |
| **OOF Calibration (`Protokol A`)** | **Deferred** *(Known Limitation)* | **Ditunda (*deferred*) dan bukan persyaratan baseline pertama.** Belum siap digunakan sampai protokol *nested training* dan *calibration* divalidasi. |
| **`UD-01` — Multiclass vs Multi-Label pada Task 3** | **Pending evidence** *(Baseline Settled: Multiclass)* | Baseline awal menggunakan **multiclass** pada label memenuhi syarat; eksperimen pembanding multi-label (bila diperlukan di tahap berikutnya) wajib menggunakan **`inner_val`** (bukan `val_cal` atau `val_thresh`). |
| **`UD-03` — Fragmentasi Label Sinonim/Typo Task 3** | **Pending evidence** | `Healty leaf` vs `None (Healthy)`, `Leaf curll`, `Yelllow Mosaic virus` menunggu audit confusion matrix Stage 8 & persetujuan perubahan mapping bila diperlukan. |
| **`UD-04` — Status 2 Kelas `Yellow Disease` (`provisional`)** | **Pending evidence** | Membutuhkan verifikasi visual/metadata karena ketiadaan `data.yaml`; dikeluarkan dari baseline utama deteksi (70 kelas). |
| **`UD-05` — Evaluasi Pipeline Gabungan (Jalur 2 Protocol B vs *Unified Split*)** | **Requires user decision** | Jalur 2 Protocol B (+ 15% `inner_val`) menyusutkan data latih Condition/Disease hingga -55,6% dan Species hingga -44,6%; pembuatan *unified split* baru membutuhkan persetujuan eksplisit pengguna. |

---

## 7. Checklist Konsistensi & Verifikasi Final Targeted Revision

### A. Checklist Verifikasi Wajib (Status: `VERIFIED` / `NOT VERIFIED` / `REQUIRES USER DECISION`)

| No | Pertanyaan Pemeriksaan | Status | Bukti & Catatan Audit |
| :-: | :--- | :---: | :--- |
| 1 | Apakah jumlah data baseline 68 single-species sudah diverifikasi? | **VERIFIED** | Terverifikasi langsung dari `split_manifest.csv`: **49.523 gambar unik** (Train 37.408 / Val 6.068 / Test 6.047) + **107 gambar** 37 label kombinasi (Train 92 / Val 0 / Test 15) = **49.630** aktif (0 duplikasi hitung). |
| 2 | Apakah jumlah gambar dan `meta_component_id` sudah konsisten? | **VERIFIED** | Baseline 68 single-species memiliki tepat **25.930 `meta_component_id` unik** (Train 19.447 + Val 3.241 + Test 3.242 = 25.930, 0 overlap antar split). Validation groups Task 1–4 juga terverifikasi (Task 1: 3.241 mc; Task 2: 2.204 mc; Task 3: 2.206 mc; Task 4A: 1.454 mc). |
| 3 | Apakah protokol OOF & eksklusi evaluasi mencakup seluruh model yang digunakan (**Species, Condition, Disease, Detection**)? | **VERIFIED** *(Proposed Protocol)* | Protokol A (5-fold OOF untuk *training/stacking features*) dan Protokol B (eksklusi penuh $E_{\text{test}}$ & $E_{\text{val}}$) pada `baseline_experiment_plan.md` Bagian 2E mencakup **Species Identification**, **Condition Classification**, **Disease/Symptom Diagnosis**, serta **Object/Leaf Detection** (bila dipakai dalam pipeline/ROI). |
| 4 | Apakah validation dan locked test bebas dari paparan training model upstream? | **REQUIRES USER DECISION** *(Proposed Protocol — belum dieksekusi)* | Protokol B mewajibkan base model untuk `val_cal`/`val_thresh`/`E_test` tidak dilatih pada `E_val ∪ E_test`, yang menyusutkan data training hingga -47,7% pada Condition/Disease dan -34,7% pada Species (*derived calculation*). Pilihan Protokol B vs *unified split* baru berstatus `REQUIRES USER DECISION` (`UD-05`). |
| 5 | Apakah common subset dijelaskan dengan batasan yang benar? | **VERIFIED** *(Verified from existing artifact)* | Istilah telah direvisi menjadi **`Three-Classifier Common Evaluation Subset`** (50 Val [40 mc, 11 spesies, 19 penyakit] / 41 Test [31 mc, 10 spesies, 15 penyakit]), secara eksplisit dibatasi hanya sebagai *sanity check* 3 classifier inti dan **bukan** evaluasi end-to-end bebas leakage bila Detection ikut dipakai (1 mc Test overlap dengan `train` Detection). |
| 6 | Apakah `val_cal` dan `val_thresh` sudah memiliki protokol yang dapat direproduksi? | **VERIFIED** *(Intra-Task)* / **UNRESOLVED** *(Multi-Task Stratification)* | `val_cal` (Fold 0, Temperature Scaling) dan `val_thresh` (Fold 1, threshold selection) adalah partisi terencana dari **`E_val_clean`** (`E_val \ E_test`), **bukan** artefak Stage 6, dengan `CALIBRATION_SPLIT_SEED = 42` dan pemisahan `inner_val` untuk early stopping/model selection. `StratifiedGroupKFold` hanya untuk mode single-task; metode stratifikasi multi-task pada `E_val_clean` berstatus **`Unresolved`**. |
| 7 | Apakah seluruh keputusan Stage 7 sebelumnya tetap konsisten? | **VERIFIED** | Seluruh keputusan arsitektur sebelumnya dipertahankan (Task 3 multiclass baseline + multi-label eksperimen terpisah, 3 kelas train-only tidak diklaim teruji, label sumber tidak diubah, full-image baseline vs ROI eksperimen, 70 kelas deteksi terverifikasi vs 2 provisional, status konseptual API/ONNX/TFLite/Flutter). |
| 8 | Apakah `Dataset/`, `daunku_app/`, manifest, mapping, dan split tidak berubah? | **VERIFIED** | Terverifikasi lewat `git status --short`: hanya 4 file laporan Stage 7 di `daunku_ai/reports/` yang berstatus untracked; **0 perubahan** pada `Dataset/`, `daunku_app/`, `canonical_manifest.csv`, `label_mapping.yaml`, split Stage 6, maupun dokumen Stage 3.1–6.1. |

### B. Ringkasan Konsistensi Lintas-Dokumen

| Item Konsistensi | `model_architecture_recommendation.md` | `baseline_experiment_plan.md` | `model_pipeline_diagram.md` | Status |
| :--- | :---: | :---: | :---: | :---: |
| Jumlah kelas & baseline 68 single-species (49.523 img / 25.930 mc) | ✅ | ✅ | ✅ | **KONSISTEN** |
| Dataset & split counts (termasuk `goletplant` 26.006, `v3i` 2.830) | ✅ | ✅ | ✅ | **KONSISTEN** |
| Imbalance Condition (18,51% vs 81,49%, rasio 1 : 4,40) | ✅ | ✅ | ✅ | **KONSISTEN** |
| Candidate architectures (`EfficientNet-B0`, `MobileNetV3-Small/Large`, `ResNet50`, `YOLOv8n`, `YOLO11n`) | ✅ | ✅ | ✅ | **KONSISTEN** |
| Protokol Group-Aware OOF seluruh model upstream & `Three-Classifier Common Evaluation Subset` | ✅ | ✅ | ✅ | **KONSISTEN** |
| Species-aware gating (5 eksperimen G1–G5, 4 kondisi Top-$k$, 95 *observed pairs*) | ✅ | ✅ | ✅ | **KONSISTEN** |
| Calibration & threshold (`val_cal`/`val_thresh` 8 poin, Locked Test steril) | ✅ | ✅ | ✅ | **KONSISTEN** |
| Detection & ROI policy (Full-image baseline, ROI eksperimen, no IoU threshold) | ✅ | ✅ | ✅ | **KONSISTEN** |
| 11 tahap pipeline, **6 Terminal `result_state`** + **Metadata `detection_state`**, `INVALID_INPUT` berhenti di validasi, full-image 1x | ✅ | ✅ | ✅ | **KONSISTEN** |
| Status konseptual API/ONNX/TFLite/KB/Flutter & `trained_model_version: null` | ✅ | ✅ | ✅ | **KONSISTEN** |

---

## 8. Daftar Perubahan pada Ketiga Dokumen Stage 7

1. **`reports/model_architecture_recommendation.md`:** Menambahkan audit *cross-task leakage* terverifikasi; merekonsiliasi 103 vs 105 kelas Species ID serta 26.006 vs 26.063 (`goletplant`) dan 2.830 vs 2.773 (`v3i`); memisahkan 68 single-species vs 37 kombinasi dan 70 kelas deteksi terverifikasi vs 2 `Yellow Disease` provisional; memperjelas 95 *observed annotation pairs*, 48 spesies non-disease (termasuk `Coffee`), 5 eksperimen gating, 4 kondisi Top-$k$, kebijakan full-image vs ROI, dan tabel `Unresolved Design Decisions`.
2. **`reports/baseline_experiment_plan.md`:** Menyelaraskan seluruh angka split & kelas; menambahkan pemisahan baseline 68 single-species dan baseline deteksi 4A (70 kelas terverifikasi) vs 4B (`Yellow Disease` provisional); menambahkan 5 skenario gating (G1–G5) berbasis *group-aware OOF*; memperjelas *group-aware* `val_cal`/`val_thresh` untuk kalibrasi & threshold; mempertegas *Natural-Background Holdout* pasca-pembekuan; serta melengkapi seluruh atribut eksperimen dan expected output artifacts.
3. **`reports/model_pipeline_diagram.md`:** Memperbarui flowchart & sequence diagram mencakup 11 tahap pipeline, **6 Terminal `result_state`** (`INVALID_INPUT` berhenti di validasi, tidak ke KB; `SPECIES_UNCERTAIN`; `OUT_OF_PATHOLOGY_SCOPE`; `HEALTHY`; `UNCERTAIN_DISEASE`; `DISEASE_INDICATION`), dan **Metadata `detection_state`** (`DETECTION_SUCCEEDED`, `DETECTION_NOT_AVAILABLE`, `DETECTION_SKIPPED`); full-image baseline berjalan 1x; ROI eksperimen terpisah; mempertahankan output Species & Condition saat Disease out-of-scope; serta memisahkan `planned_model_version` vs `trained_model_version: null`.

---

## 9. Status Penutupan Stage 7

**Status Akhir:** **`STAGE 7 COMPLETE`** *(Tidak ada critical blocker untuk memulai baseline pertama Stage 8).*

Seluruh kriteria penutupan Stage 7 telah terpenuhi: arsitektur baseline terpilih dan terdokumentasi, setiap task memiliki baseline experiment plan yang dapat dijalankan, kelayakan dan keterbatasan dataset terverifikasi dari artefak aktual, pemisahan fungsi validasi (`inner_val` / `val_cal` / `val_thresh` / `E_test`) tidak saling bertentangan, seluruh klaim deployment/API tetap berstatus *planned/conceptual*, serta hal yang belum diketahui diberi status *deferred* atau *known limitation* (termasuk OOF calibration, 37 kombinasi multi-spesies, discrepancy 149 kelas Detection, dan evaluasi ulang *unified split* saat integrasi multi-model diperlukan). **Stage 8 hanya dapat dimulai setelah persetujuan eksplisit dari pengguna.**
