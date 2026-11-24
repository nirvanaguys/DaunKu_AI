# Ringkasan Metodologi Sampling Visual & Indeks Contact Sheet (Tahap 4) — DaunKu AI

> **Waktu Audit:** 2026-11-24 02:12:03  
> **Random Seed:** `42` (Reproducible deterministic sampling)  
> **Total Gambar Diaudit:** 85.022 file  
> **Total Lembar Kontak Dihasilkan:** 20 contact sheets  

---

## 1. Metodologi dan Rasionalitas Sampling

1. **Prinsip Keterwakilan (Stratified Sampling):**
   - Untuk setiap dataset dari 14 dataset, sampel diambil secara berstrata mencakup seluruh kelas utama yang memiliki proporsi terbesar hingga minoritas.
   - Jumlah sampel dibatasi 16 gambar per lembar kontak (grid 4x4) agar setiap gambar memiliki ruang thumbnail $220\times220$ piksel yang cukup tajam untuk inspeksi visual mata manusia.

2. **Kelompok Uji Khusus Anomali (Targeted Anomaly Sampling):**
   - Selain sampel representatif acak per dataset, dibuat 6 lembar kontak khusus yang secara deterministik menyaring kandidat gambar ekstrem:
     - **Suspect Blur:** Menyaring gambar dengan Variance of Laplacian terkecil ($< 50.0$) pada skala normalisasi $256\times256$.
     - **Too Dark (Underexposed):** Menyaring gambar dengan kecerahan rata-rata $< 35.0$.
     - **Too Bright (Overexposed):** Menyaring gambar dengan kecerahan rata-rata $> 220.0$.
     - **Extreme Aspect Ratio:** Menyaring gambar dengan rasio lebar:tinggi $< 0.40$ atau $> 2.50$.
     - **Synthetic No-BG vs Natural:** Membandingkan gambar hasil pemotongan latar belakang otomatis (`no_bg_`) dengan foto berlatar alami.
     - **Low Resolution:** Menyaring gambar dengan dimensi $< 224\times224$ piksel.

3. **Keterbatasan dan Interpretasi Indikator Sampling:**
   - **Variance of Laplacian:** Berfungsi sebagai penyaring heuristik kandidat gambar blur pada resolusi $256\times256$. Nilai rendah ($<50,0$) tidak selalu membuktikan gambar rusak; daun bertekstur halus tanpa tulang daun tegas secara alami dapat memiliki skor Laplacian rendah.
   - **Ambang Kecerahan (Brightness):** Merupakan indikator pencahayaan kamera ($<35,0$ underexposed, $>220,0$ overexposed), bukan bukti kerusakan file. Sebagian besar gambar underexposed masih dapat dipulihkan dengan teknik adaptif kontras (CLAHE).
   - **Format-Extension Mismatch:** Menunjukkan ketidakcocokan antara header biner (PNG) dengan ekstensi file (.jpg), bukan kerusakan konten piksel.
   - **Representasi Visual:** Lembar kontak menyajikan sampel kualitatif terfokus (16 gambar per lembar) untuk memverifikasi pola visual. Kesimpulan populasi tetap bersumber dari komputasi lengkap seluruh 85.022 file di `image_quality_issues.csv`.

---

## 2. Indeks Lembar Kontak Visual (`reports/image_samples/`)

| File Lembar Kontak | Deskripsi Isi & Kategori | Jumlah Sampel |
| :--- | :--- | :---: |
| [`cs_01_A_dataset_of_Yellow_Disea.jpg`](cs_01_A_dataset_of_Yellow_Disea.jpg) | Sampel representatif kelas dari dataset A dataset of Yellow Disease in Horticultural Plant | 16 gambar |
| [`cs_02_Arabian_Jasmine_Leaf_Cond.jpg`](cs_02_Arabian_Jasmine_Leaf_Cond.jpg) | Sampel representatif kelas dari dataset Arabian Jasmine Leaf Condition Dataset (AJLCD-2025 | 16 gambar |
| [`cs_03_Houseplants_Image_Detecti.jpg`](cs_03_Houseplants_Image_Detecti.jpg) | Sampel representatif kelas dari dataset Houseplants Image Detection.v1i.tensorflow | 16 gambar |
| [`cs_04_Klasifikasi_Penyakit_Daun.jpg`](cs_04_Klasifikasi_Penyakit_Daun.jpg) | Sampel representatif kelas dari dataset Klasifikasi Penyakit Daun Kopi.v4i.tensorflow | 16 gambar |
| [`cs_05_Leaf_Image_Dataset_for_Pl.jpg`](cs_05_Leaf_Image_Dataset_for_Pl.jpg) | Sampel representatif kelas dari dataset Leaf Image Dataset for Plant disease Classificatio | 16 gambar |
| [`cs_06_Perfect_Data_Set.jpg`](cs_06_Perfect_Data_Set.jpg) | Sampel representatif kelas dari dataset Perfect Data Set | 16 gambar |
| [`cs_07_Plant_Classification_and.jpg`](cs_07_Plant_Classification_and.jpg) | Sampel representatif kelas dari dataset Plant Classification and Disease.v1i.tensorflow | 16 gambar |
| [`cs_08_Plant_Classification_and.jpg`](cs_08_Plant_Classification_and.jpg) | Sampel representatif kelas dari dataset Plant Classification and Disease.v3i.tensorflow | 16 gambar |
| [`cs_09_Potato_Leaf_Disease_Datas.jpg`](cs_09_Potato_Leaf_Disease_Datas.jpg) | Sampel representatif kelas dari dataset Potato Leaf Disease Dataset in Uncontrolled Environment | 16 gambar |
| [`cs_10_Rose_And_MArigold_Leaf_Di.jpg`](cs_10_Rose_And_MArigold_Leaf_Di.jpg) | Sampel representatif kelas dari dataset Rose And MArigold Leaf Disease 1 | 16 gambar |
| [`cs_11_Rubber_Leaf_Dataset.jpg`](cs_11_Rubber_Leaf_Dataset.jpg) | Sampel representatif kelas dari dataset Rubber_Leaf_Dataset | 16 gambar |
| [`cs_12_Tomato_leaf_diseases.jpg`](cs_12_Tomato_leaf_diseases.jpg) | Sampel representatif kelas dari dataset Tomato leaf diseases | 16 gambar |
| [`cs_13_dataset_for_various_disea.jpg`](cs_13_dataset_for_various_disea.jpg) | Sampel representatif kelas dari dataset dataset for various disease detection of Rose ,Tagetes erecta  Hibiscus rosa-sinensis | 16 gambar |
| [`cs_14_goletplant_v5i_tensorflow.jpg`](cs_14_goletplant_v5i_tensorflow.jpg) | Sampel representatif kelas dari dataset goletplant.v5i.tensorflow | 16 gambar |
| [`cs_anomaly_blur_suspects.jpg`](cs_anomaly_blur_suspects.jpg) | Kandidat gambar kabur/blur (6,042 terdeteksi) | 16 gambar |
| [`cs_anomaly_too_dark.jpg`](cs_anomaly_too_dark.jpg) | Kandidat gambar underexposed (11,191 terdeteksi) | 16 gambar |
| [`cs_anomaly_too_bright.jpg`](cs_anomaly_too_bright.jpg) | Kandidat gambar overexposed/washout (5,895 terdeteksi) | 16 gambar |
| [`cs_anomaly_extreme_aspect.jpg`](cs_anomaly_extreme_aspect.jpg) | Kandidat rasio aspek ekstrem (13 terdeteksi) | 13 gambar |
| [`cs_bias_synthetic_nobg_vs_natural.jpg`](cs_bias_synthetic_nobg_vs_natural.jpg) | Perbandingan bias background removal sintetis vs latar alami | 16 gambar |
| [`cs_anomaly_small_resolution.jpg`](cs_anomaly_small_resolution.jpg) | Kandidat resolusi rendah (<224x224, 34 terdeteksi) | 16 gambar |

---
*Seluruh thumbnail pada lembar kontak di atas dapat dilacak kembali ke file sumber di `Dataset/` menggunakan path relatif di `reports/image_quality_issues.csv`.*
