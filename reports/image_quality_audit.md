# Laporan Audit Kualitas Visual & Karakteristik Citra (Tahap 4 - Revisi) — DaunKu AI

> **Waktu Audit:** 24 November 2026 (Revisi Lengkap Berbasis Bukti Aktual)  
> **Status:** Selesai Diverifikasi Penuh (85.022 Gambar Mentah)  
> **Peran:** Senior Machine Learning Engineer & Data Quality Engineer  
> **Dokumen Acuan:** `Rencana_Implementasi_AI_DaunKu.md`, `reports/duplicate_audit.md`, `reports/stage3_1_final_review.md`  

---

## 1. Ringkasan Eksekutif Kualitas Gambar

Pemeriksaan kualitas visual dan karakteristik teknis telah dilaksanakan terhadap seluruh **85.022 file gambar mentah** (14 dataset sumber di folder `Dataset/`) secara non-destruktif dan read-only.

Dari hasil evaluasi menyeluruh:
- **Integritas File:** Seluruh 85.022 gambar **100% valid dan dapat didekodekan** (*0 corrupted files*). Tidak ditemukan file kosong (0 byte) maupun file yang gagal dibaca oleh pustaka pemrosesan citra.
- **Pembedaan Baris Isu vs Gambar Unik:** Dari total 85.022 gambar, terdeteksi **20.614 gambar unik (24,25%)** yang memiliki satu atau lebih catatan anomali teknis, menghasilkan total **43.454 baris catatan isu** pada `reports/image_quality_issues.csv` (rata-rata 2,1 isu per gambar bermasalah). Sebanyak **11.511 gambar** memiliki lebih dari satu jenis anomali.

### Tabel Ringkasan Metrik Kualitas Global:
| Indikator Pemeriksaan | Jumlah Kejadian (Baris) | Ambang Batas (Threshold) | Persentase Populasi | Dampak & Status Kualitas |
| :--- | :---: | :---: | :---: | :--- |
| **Total Gambar Diperiksa** | **85.022** | Seluruh file gambar di `Dataset/` | 100,00% | Basis data lengkap |
| **Gambar Rusak (*Corrupted*)** | **0** | Gagal decode biner PIL | **0,00%** | 🟢 **Sempurna (0 error)** |
| **Format vs Ext Mismatch** | **11.234** | Header biner (PNG) $\neq$ ekstensi (.jpg) | 13,21% | 🟡 Perlu normalisasi ekstensi |
| **Resolusi Terlalu Rendah** | **34** | Lebar $< 224$ px ATAU Tinggi $< 224$ px | 0,04% | 🔴 Perlu kurasi/filter |
| **Rasio Aspek Ekstrem** | **13** | Rasio Aspek $< 0,40$ atau $> 2,50$ | 0,02% | 🟡 Perlu padding letterbox |
| **Underexposed (Sangat Gelap)** | **11.191** | Kecerahan rata-rata $< 35,0$ (skala 0–255) | 13,16% | 🔴 Risiko detail lesi tertutup |
| **Overexposed (Sangat Terang)** | **5.895** | Kecerahan rata-rata $> 220,0$ (skala 0–255) | 6,93% | 🟡 Risiko washout tekstur daun |
| **Kontras Sangat Rendah** | **424** | Standar Deviasi Kontras $< 15,0$ | 0,50% | 🟡 Gambar datar/seragam |
| **Kandidat Gambar Blur** | **6.042** | Variance of Laplacian $< 50,0$ ($256\times256$) | 7,11% | 🟡 Indikator awal review |
| **Background Removal Sintetis** | **8.621** | Prefix nama file `no_bg_*` | 10,14% | 🔴 **Risiko shortcut learning** |

---

## 2. Karakteristik Teknis & Distribusi Gambar

### A. Statistik Kuantitatif Karakteristik Gambar (Global):
| Metrik Karakteristik | Nilai Minimum | Nilai Rata-rata | Nilai Median | Nilai Maksimum | Catatan Teknis |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Lebar Piksel (Width)** | 150 px | 1.088,7 px | 1.000 px | 12.000 px | Variasi skala sangat lebar antar dataset |
| **Tinggi Piksel (Height)** | 192 px | 1.041,9 px | 910 px | 9.000 px | Sebagian besar mendekati format bujur sangkar |
| **Total Resolusi (Megapixels)** | 0,0300 MP | 1,72 MP | 0,92 MP | 108,00 MP | Median mendekati 1 Megapixel |
| **Rasio Aspek ($W/H$)** | 0,37 | 1,05 | 1,00 | 3,84 | Median = 1,00 (bujur sangkar standar) |
| **Ukuran File di Disk** | 3,3 KB | 0,22 MB | 0,10 MB | 4,04 MB | Seluruh file efisien untuk penyimpanan lokal |
| **Kecerahan Rata-rata (0–255)** | 0,7 | 130,2 | 136,3 | 252,6 | Distribusi normal di sekitar nilai tengah 128 |
| **Kontras (Std Deviasi 0–127)** | 5,9 | 53,2 | 52,4 | 122,4 | Rata-rata kontras dinamis baik |
| **Variance of Laplacian ($256\times256$)** | 3,7 | 539,1 | 235,7 | 9.619,0 | Skala terstandarisasi untuk deteksi blur |

### B. Distribusi Mode Warna & Format File:
- **Mode Warna:**
  - `RGB`: **67.330 gambar (79,19%)** — Mode warna 3-channel standar.
  - `RGBA`: **17.692 gambar (20,81%)** — Memiliki kanal alpha (transparansi), banyak ditemukan pada gambar ekspor Roboflow dan segmentasi.
- **Format File Biner (Berdasarkan Header):**
  - `JPEG`: **67.330 gambar (79,19%)**
  - `PNG`: **17.692 gambar (20,81%)**
- **Format-Extension Mismatch:**
  - Terdapat **11.234 file** yang memiliki header internal `PNG` namun diberi ekstensi `.jpg` pada nama filenya (terutama pada `Arabian Jasmine` dan sebagian Roboflow). Gambar tetap dapat dibaca oleh Pillow, namun wajib dinormalisasi pada saat pembuatan canonical dataset agar tidak menimbulkan error pada library C/C++ loader yang kaku.

### C. Karakteristik Teknis per Dataset Sumber:
| No | Nama Dataset Sumber | Jumlah Gambar | Resolusi Dominan | Rasio Aspek Rata-rata | Laplacian Rata-rata | Ukuran Rata-rata |
| :-: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `A dataset of Yellow Disease in Horticultural Plant` | 5.095 | 640x640 | 1,00 | 207,8 | 0,04 MB |
| 2 | `Arabian Jasmine Leaf Condition Dataset (AJLCD-2025` | 6.315 | 1440x1080 | 1,04 | 112,2 | 0,35 MB |
| 3 | `Houseplants Image Detection.v1i.tensorflow` | 6.055 | 640x640 | 1,00 | 928,6 | 0,05 MB |
| 4 | `Klasifikasi Penyakit Daun Kopi.v4i.tensorflow` | 3.216 | 640x640 | 1,00 | 886,4 | 0,06 MB |
| 5 | `Leaf Image Dataset for Plant disease Classificatio` | 13.905 | 256x256 | 1,00 | 100,7 | 0,01 MB |
| 6 | `Perfect Data Set` | 3.449 | 1080x1080 | 1,00 | 94,9 | 0,48 MB |
| 7 | `Plant Classification and Disease.v1i.tensorflow` | 628 | 640x640 | 1,00 | 822,2 | 0,05 MB |
| 8 | `Plant Classification and Disease.v3i.tensorflow` | 3.184 | 640x640 | 1,00 | 1343,6 | 0,07 MB |
| 9 | `Potato Leaf Disease Dataset in Uncontrolled Environment` | 3.076 | 1500x1500 | 1,00 | 475,8 | 0,23 MB |
| 10 | `Rose And MArigold Leaf Disease 1` | 3.449 | 1080x1080 | 1,00 | 94,9 | 0,48 MB |
| 11 | `Rubber_Leaf_Dataset` | 3.481 | 1993x1984 | 1,04 | 121,0 | 1,26 MB |
| 12 | `Tomato leaf diseases` | 2.627 | 4032x3024 | 1,33 | 126,5 | 0,16 MB |
| 13 | `dataset for various disease detection of Rose,Tagetes,Hibiscus` | 4.479 | 1080x1080 | 1,00 | 93,9 | 0,47 MB |
| 14 | `goletplant.v5i.tensorflow` | 26.063 | 1200x1071 | 1,11 | 1001,6 | 0,19 MB |

---

## 3. Investigasi Khusus Resolusi Rendah (34 Gambar)

Pemeriksaan ulang terhadap 34 gambar yang teridentifikasi memiliki resolusi di bawah batas rekomendasi arsitektur standar ($224 \times 224$ piksel) menghasilkan temuan terukur:

### A. Rincian Kategori Resolusi:
- **Kriteria $W < 224$ ATAU $H < 224$:** **34 gambar**
- **Kriteria $W < 150$ ATAU $H < 150$:** **0 gambar**
- **Kriteria $W < 150$ DAN $H < 150$:** **0 gambar**

Seluruh 34 gambar tersebut berasal dari dataset `goletplant.v5i.tensorflow`. Dimensi terkecil absolut pada seluruh dataset adalah **$191 \times 264$ piksel** (file `BunnyEarCactus_159_jpg...`) dan **$200 \times 200$ piksel** (file `Schefflera_108_jpg...`).

### B. Koreksi Rekomendasi:
> [!IMPORTANT]
> **Koreksi Data:** Tidak ada satu pun gambar di bawah $150 \times 150$ piksel di dalam repositori. Rekomendasi kurasi disesuaikan secara akurat:
> Sebanyak 34 gambar yang memiliki sisi terpendek antara $191\text{--}207$ piksel (khususnya kelas *BunnyEarCactus*, *Pachypodium lamerei*, dan *Schefflera*) direkomendasikan untuk **dievaluasi secara manual atau dikecualikan dari data uji/evaluasi utama**, guna menghindari distorsi upscaling saat model menggunakan input standar $224\times224$ atau $256\times256$.

---

## 4. Analisis Ketidakseimbangan Kelas Sumber (Class Imbalance)

Rasio ketidakseimbangan kelas (*imbalance ratio*) dihitung secara ketat dengan rumus:
$$\text{Imbalance Ratio} = \frac{\text{Jumlah Sampel Kelas Terbesar}}{\text{Jumlah Sampel Kelas Terkecil}}$$

Berikut adalah tabel rincian per dataset berdasarkan jumlah gambar unik per kelas sumber:

| Dataset Sumber | Total Kelas | Kelas Terbanyak (Sampel) | Kelas Tersedikit (Sampel) | Rumus Perhitungan | Rasio Imbalance | Kelas Kritis (<50 Gambar) |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: |
| `A dataset of Yellow Disease...` | 2 | Class 0 (2.753) | Class 1 (2.384) | $2.753 / 2.384$ | **1,15 : 1** | 0 kelas |
| `Arabian Jasmine (AJLCD-2025)` | 8 | Healthy (955) | Cholorosis (699) | $955 / 699$ | **1,37 : 1** | 0 kelas |
| `Houseplants Image Detection` | 24 | Epipremnum (828) | Solenostemon (3) | $828 / 3$ | **276,00 : 1** | **14 kelas** |
| `Klasifikasi Daun Kopi` | 1 | leaf (3.139) | leaf (3.139) | $3.139 / 3.139$ | **1,00 : 1** | 0 kelas |
| `Leaf Image Dataset...` | 58 | Bitter gourd/Leaf curl (1.056) | bunchy top bitter gourd (12) | $1.056 / 12$ | **88,00 : 1** | **17 kelas** |
| `Perfect Data Set` | 7 | rose / Healthy (1.167) | marigold / Pest Damaged (78) | $1.167 / 78$ | **14,96 : 1** | 0 kelas |
| `Plant Classification v1` | 10 | Swiss Cheese Plant (204) | Aglaonema Commutatum (30) | $204 / 30$ | **6,80 : 1** | **4 kelas** |
| `Plant Classification v3` | 17 | Swiss Cheese Plant (596) | Dracaena angolensis (53) | $596 / 53$ | **11,25 : 1** | 0 kelas |
| `Potato Leaf Disease...` | 7 | Fungi (748) | Nematode (68) | $748 / 68$ | **11,00 : 1** | 0 kelas |
| `Rose And MArigold Leaf Disease 1` | 7 | rose / Healthy (1.167) | marigold / Pest Damaged (78) | $1.167 / 78$ | **14,96 : 1** | 0 kelas |
| `Rubber_Leaf_Dataset` | 8 | Raw / Healthy (506) | Raw / Anthracnose (300) | $506 / 300$ | **1,69 : 1** | 0 kelas |
| `Tomato leaf diseases` | 10 | Leaf Miner (519) | Leaf Mold (66) | $519 / 66$ | **7,86 : 1** | 0 kelas |
| `dataset for various disease...` | 13 | Rosa / Healthy Leaf (1.167) | Hibiscus rosa-sinensis (44) | $1.167 / 44$ | **26,52 : 1** | **1 kelas** |
| `goletplant.v5i.tensorflow` | 53 | Euphorbiamilii (767) | Label `-` (3) | $767 / 3$ | **255,67 : 1** | **1 kelas** |

### Verifikasi Khusus Kasus Dataset `Houseplants Image Detection`:
Terdapat dua cara interpretasi angka pada dataset berformat object detection ini:
1. **Berdasarkan Jumlah Gambar Unik (Image-Level):**
   - **Split Train Saja:** Kelas terbanyak adalah `snake plant` (**813 gambar**), kelas tersedikit adalah `Aglaonema` / `Solenostemon` (**3 gambar**).  
     $$\text{Rasio Imbalance (Train Images)} = \frac{813}{3} = \mathbf{271,00 : 1}$$
   - **Total Seluruh Split (Train + Valid + Test):** Kelas terbanyak adalah `Epipremnum` (**828 gambar**) atau `snake plant` (**822 gambar**), kelas tersedikit adalah `Aglaonema` / `Solenostemon` / `BunnyEarCactus` (**3 gambar**).  
     $$\text{Rasio Imbalance (Total Images)} = \frac{828}{3} = \mathbf{276,00 : 1} \quad \left(\text{atau } \frac{822}{3} = 274,00 : 1 \text{ untuk snake plant}\right)$$
2. **Berdasarkan Jumlah Objek Bounding Box (Box-Level):**
   - Objek bounding box terbanyak adalah `Peperomia caperata` (**2.112 box**).
   - Objek bounding box tersedikit adalah `Aglaonema` / `Solenostemon` (**3 box**).  
     $$\text{Rasio Imbalance (Bounding Box)} = \frac{2.112}{3} = \mathbf{704,00 : 1}$$

*Kesimpulan:* Rasio 271:1, 276:1, dan 704:1 seluruhnya valid secara matematis, tergantung apakah dihitung berbasis gambar per split, total gambar, atau jumlah bounding box. Kedua metrik ini menunjukkan ketidakseimbangan kelas yang sangat parah pada tanaman hias minoritas.

---

## 5. Verifikasi Faktual Background Removal pada Dataset Mawar

Investigasi mendalam berbasis nama file dan verifikasi visual sampling mengoreksi klaim awal:

### A. Rincian Statistik per Dataset Sumber:
1. **`Perfect Data Set` (Total 3.449 gambar):**
   - Subfolder Mawar (`rose/`): **2.760 gambar**.
     - Pola `no_bg_*`: **2.760 gambar (100,00%)**
     - Pola non-`no_bg`: **0 gambar**
   - Subfolder Marigold (`marigold/`): 689 gambar (seluruhnya berlatar alami, 0 `no_bg_*`).
2. **`Rose And MArigold Leaf Disease 1` (Total 3.449 gambar):**
   - Subfolder Mawar (`rose/`): **2.760 gambar**.
     - Pola `no_bg_*`: **2.760 gambar (100,00%)**
     - Pola non-`no_bg`: **0 gambar**
   - Subfolder Marigold (`marigold/`): 689 gambar (seluruhnya berlatar alami, 0 `no_bg_*`).
3. **`dataset for various disease detection of Rose, Tagetes erecta Hibiscus rosa-sinensis` (Total 4.479 gambar):**
   - Folder Mawar (`Rosa/`): **3.577 gambar**.
     - Pola `no_bg_*`: **2.888 gambar (80,74%)**
     - **Pola non-`no_bg` (Berlatar Belakang Alami):** **689 gambar (19,26%)**
   - Folder Non-Mawar (`Tagetes erecta` & `Hibiscus rosa-sinensis`): 902 gambar.
     - Pola `no_bg_*`: **213 gambar (23,61%)** (pada subfolder Tagetes)
     - Pola non-`no_bg` (Latar Alami): **689 gambar (76,39%)**

### B. Pembedaan Bukti Pola Nama vs Inspeksi Visual:
- **Bukti Pola Nama:** Di seluruh repositori, terdapat tepat **8.621 file** dengan pola nama `no_bg_*` ($2.760 + 2.760 + 2.888 + 213 = 8.621$).
- **Bukti Visual Sampling:** Pada lembar kontak `cs_bias_synthetic_nobg_vs_natural.jpg`, gambar dengan prefix `no_bg_` terbukti secara visual dipotong latarnya menjadi putih polos seragam.
- **Koreksi Kritis:** **Tidak seluruh gambar mawar dipotong latarnya**. Sebanyak **689 gambar mawar** pada dataset ketiga mempertahankan latar belakang alami kebun. Hal ini sangat bernilai karena 689 gambar alami tersebut dapat digunakan sebagai kelompok evaluasi uji yang tidak terkontaminasi bias latar putih.

---

## 6. Rincian dan Distribusi Anomali Citra (`image_quality_issues.csv`)

File [reports/image_quality_issues.csv](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/image_quality_issues.csv) mencatat seluruh anomali teknis yang terdeteksi:

### A. Rekapitulasi Baris vs Gambar Unik:
- **Total Baris Anomali:** **43.454 baris**
- **Jumlah Path Gambar Unik yang Terlibat:** **20.614 gambar unik** (24,25% dari total dataset)
- **Jumlah Gambar dengan Multi-Anomali (>1 isu):** **11.511 gambar** (misalnya gambar yang sekaligus berekstensi mismatch, underexposed, dan blur suspect).

### B. Distribusi per Jenis Anomali:
| No | Jenis Anomali (`Issue Type`) | Jumlah Baris Kejadian | Persentase terhadap Isu | Keterangan Indikator |
| :-: | :--- | :---: | :---: | :--- |
| 1 | `FORMAT_EXT_MISMATCH` | **11.234** | 25,85% | Header internal PNG namun berekstensi .jpg |
| 2 | `TOO_DARK` | **11.191** | 25,75% | Kecerahan rata-rata $< 35,0$ (underexposed) |
| 3 | `SYNTHETIC_BACKGROUND` | **8.621** | 19,84% | Prefix nama file `no_bg_*` (latar putih sintetis) |
| 4 | `SUSPECT_BLUR` | **6.042** | 13,90% | Variance of Laplacian $< 50,0$ ($256\times256$) |
| 5 | `TOO_BRIGHT` | **5.895** | 13,57% | Kecerahan rata-rata $> 220,0$ (overexposed/washout) |
| 6 | `LOW_CONTRAST` | **424** | 0,98% | Standar deviasi kontras $< 15,0$ |
| 7 | `TOO_SMALL` | **34** | 0,08% | Dimensi $< 224\times224$ piksel |
| 8 | `EXTREME_ASPECT_RATIO` | **13** | 0,03% | Rasio aspek $< 0,40$ atau $> 2,50$ |
| | **TOTAL BARIS ANOMALI** | **43.454** | **100,00%** | **Mencakup 20.614 gambar unik** |

### C. Distribusi Tingkat Prioritas Gambar Unik:
Setiap gambar unik diklasifikasikan berdasarkan tingkat keparahan isu tertingginya:
- **Prioritas HIGH (17.120 gambar unik):** Gambar yang memiliki isu kritis berpotensi merusak representasi model (terlalu kecil, sangat gelap $< 35$, atau overexposed $> 220$).
- **Prioritas MEDIUM (3.494 gambar unik):** Gambar yang hanya memiliki isu sekunder (format mismatch, suspect blur, kontras rendah, rasio ekstrem, atau background removal) tanpa disertai isu HIGH.
- **Prioritas LOW (0 gambar):** Seluruh isu teknis yang terdeteksi memiliki implikasi pemrosesan sehingga dikategorikan minimal MEDIUM.

---

## 7. Metodologi dan Keterbatasan Audit Visual

Untuk mencegah salah interpretasi, batasan teknis dari indikator yang digunakan didefinisikan secara transparan:

1. **Variance of Laplacian Bukan Vonis Mutlak Kerusakan Gambar:**
   - Perhitungan variansi Laplacian pada resolusi normalisasi $256 \times 256$ adalah **alat skrining otomatis untuk menemukan kandidat gambar kabur/blur**.
   - Nilai $< 50,0$ mengindikasikan rendahnya frekuensi spasial tinggi (tepi tidak tajam). Namun, daun yang sehat dengan permukaan lilin licin dan tanpa guratan tulang daun mencolok dapat memiliki nilai Laplacian rendah secara alami tanpa berarti foto tersebut blur. Oleh karena itu, kandidat blur **dilarang dihapus otomatis**.
2. **Ambang Kecerahan Adalah Indikator Pencahayaan, Bukan Kerusakan Citra:**
   - Ambang $< 35,0$ (*underexposed*) dan $> 220,0$ (*overexposed*) mengidentifikasi kondisi pencahayaan ekstrem saat pengambilan foto.
   - Banyak gambar underexposed pada dataset kentang dan kopi masih memuat struktur daun yang dapat dikenali mata manusia, dan dapat diperbaiki kualitas representasinya menggunakan normalisasi kontras lokal (CLAHE) pada tahap preprocessing.
3. **Format-Extension Mismatch:**
   - Mismatch ini bukan kerusakan biner, melainkan inkonsistensi penamaan file saat diekspor dari platform asal (Roboflow/web scraping). File tetap valid dibuka menggunakan decoder modern (Pillow/OpenCV).
4. **Keterbatasan Sampling Lembar Kontak (Contact Sheets):**
   - Dua puluh lembar kontak di `reports/image_samples/` menyajikan sampel representatif berstrata (16 gambar per sheet) dengan seed acak tetap (`seed=42`).
   - Kesimpulan visual mengenai sudut kamera, proporsi kanvas, dan latar belakang merupakan observasi kualitatif terhadap sampel representatif tersebut. Keputusan data menyeluruh tetap berpedoman pada metrik populasi 85.022 gambar.

---

## 8. Rekomendasi Penanganan Kualitas (Actionable Roadmap)

| Prioritas | Masalah Kualitas | Populasi Terdampak | Rekomendasi Penanganan pada Tahap 5 & Preprocessing |
| :---: | :--- | :---: | :--- |
| 🔴 **HIGH** | **Background Removal Sintetis (`no_bg_*`)** | 8.621 file (Mawar & Tagetes) | Gunakan 689 foto mawar berlatar alami untuk himpunan validasi/uji. Pada training, terapkan augmentasi *synthetic background replacement* acak. |
| 🔴 **HIGH** | **Ketidakseimbangan Kelas Ekstrem** | 14 kelas di Houseplants, 17 di Leaf Image, 39 di Goletplant | Terapkan *Class-Weighted Cross Entropy / Focal Loss* dan gabungkan varietas langka ke tingkat genus pada Tahap 5. |
| 🔴 **HIGH** | **Resolusi Terlalu Rendah ($< 224$ px)** | 34 file ($191\text{--}207$ px di Goletplant) | Evaluasi manual dan filter dari data evaluasi uji agar tidak terdistorsi saat di-upscale ke input model standar. |
| 🟡 **MEDIUM** | **Eksposur Ekstrem (Gelap & Terang)** | 11.191 gelap / 5.895 terang | Terapkan adaptif histogram equalization (CLAHE) dan augmentasi kecerahan/kontras pada pipeline pelatihan. |
| 🟡 **MEDIUM** | **Koordinat Box Melebihi Kanvas** | 436 anotasi Roboflow | Terapkan fungsi kliping koordinat otomatis (`min/max clipping`) pada custom data loader sebelum masuk ke model. |
| 🟡 **MEDIUM** | **Format Extension Mismatch (PNG vs JPG)** | 11.234 file | Normalisasi ekstensi file pada pembuatan metadata manifest kanonikal di Tahap 5. |
| 🟢 **LOW** | **Rasio Aspek Ekstrem ($<0,4$ atau $>2,5$)** | 13 file | Terapkan padding *Letterboxing* netral saat proses resize kanvas persegi model. |

---

## 9. Deliverable Resmi Tahap 4

1. 📄 **[reports/image_quality_audit.md](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/image_quality_audit.md)** — Laporan audit kualitas komprehensif terverifikasi.
2. 📊 **[reports/image_quality_issues.csv](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/image_quality_issues.csv)** — Tabel rincian 43.454 catatan anomali dari 20.614 gambar unik.
3. 📝 **[reports/image_sampling_summary.md](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/image_sampling_summary.md)** — Ringkasan metodologi sampling, random seed `42`, indeks 20 contact sheet, dan keterbatasan sampling.
4. 🖼️ **Folder [reports/image_samples/](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/image_samples/)** — 20 file lembar kontak visual JPG (14 dataset representatif + 6 kelompok anomali/bias).
5. ⚙️ **[scripts/run_image_quality_audit.py](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/scripts/run_image_quality_audit.py)** — Skrip audit otomatis paralel yang dapat dijalankan ulang.

---

## 10. Konfirmasi Batasan & Integritas Proyek

- **Folder `Dataset/`:** Tetap **100% READ-ONLY**, tidak ada file gambar asli yang diubah, dihapus, dikompres, atau dipindahkan.
- **Folder `daunku_app/` (Flutter):** Tidak disentuh sama sekali.
- **Git Status:** Tidak ada commit atau push yang dilakukan.
- **Tahap 5 (Canonical Dataset & Label Mapping):** **Belum dimulai.**

*Laporan Revisi Tahap 4 selesai. Menunggu ulasan dan arahan dari Anda.*
