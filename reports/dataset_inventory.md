# Laporan Inventaris Dataset Aktual (Tahap 1 — 15 Dataset) — DaunKu AI

> **Waktu Audit:** 23 November 2026 (Pembaruan Pasca Penambahan Dataset)  
> **Status:** Selesai  
> **Metode:** Penelusuran rekursif biner pada seluruh 15 direktori di `daunku_ai/Dataset/` & verifikasi gambar biner streaming PIL.

---

## 1. Tabel Ringkasan Inventaris 15 Dataset

| No | Nama Folder Dataset | Tipe Tugas | Format Anotasi | Total Gambar | Train | Valid | Test | Unsplit | Ukuran (MB) |
| :-: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `A dataset of Yellow Disease in Horticultural Plant` | Object Detection | YOLO Darknet / YOLOv5 (.txt per image) | **5,095** | 0 | 0 | 0 | 5,095 | 213.28 MB |
| 2 | `Arabian Jasmine Leaf Condition Dataset (AJLCD-2025` | Image Classification | Directory Structure (Folder per Class) | **6,315** | 0 | 0 | 0 | 6,315 | 2,190.1 MB |
| 3 | `Comparative Morphological and Phytochemical` | Empty / None | Empty Directory | **0** | 0 | 0 | 0 | 0 | 0.0 MB |
| 4 | `Houseplants Image Detection.v1i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **6,055** | 5,967 | 4 | 84 | 0 | 320.69 MB |
| 5 | `Klasifikasi Penyakit Daun Kopi.v4i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **3,216** | 2,804 | 263 | 149 | 0 | 189.59 MB |
| 6 | `Leaf Image Dataset for Plant disease Classificatio` | Image Classification (Archived) | ZIP Archive (Unextracted) | **0** | 0 | 0 | 0 | 0 | 83.55 MB |
| 7 | `Perfect Data Set` | Image Classification | Directory Structure (Folder per Class) | **3,449** | 0 | 0 | 0 | 3,449 | 1,649.84 MB |
| 8 | `Plant Classification and Disease.v1i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **628** | 563 | 46 | 19 | 0 | 33.65 MB |
| 9 | `Plant Classification and Disease.v3i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **3,184** | 2,921 | 178 | 85 | 0 | 222.62 MB |
| 10 | `Potato Leaf Disease Dataset in Uncontrolled Environment` | Image Classification | Directory Structure (Folder per Class) | **3,076** | 0 | 0 | 0 | 3,076 | 719.42 MB |
| 11 | `Rose And MArigold Leaf Disease 1` | Image Classification | Directory Structure (Folder per Class) | **3,449** | 0 | 0 | 0 | 3,449 | 1,649.84 MB |
| 12 | `Rubber_Leaf_Dataset` | Image Classification | Directory Structure (Folder per Class) | **3,481** | 0 | 0 | 0 | 3,481 | 4,398.8 MB |
| 13 | `Tomato leaf diseases` | Image Classification | Directory Structure (Folder per Class) | **2,627** | 0 | 0 | 0 | 2,627 | 429.86 MB |
| 14 | `dataset for various disease detection of Rose ,Tagetes erecta  Hibiscus rosa-sinensis` | Image Classification | Directory Structure (Folder per Class) | **4,479** | 0 | 0 | 0 | 4,479 | 2,096.21 MB |
| 15 | `goletplant.v5i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **26,063** | 25,373 | 22 | 668 | 0 | 4,919.25 MB |
| | **TOTAL KESELURUHAN (Mentah)** | | | **71,117** | | | | | **18.67 GB** |

---

## 2. Status Integritas File Gambar

Dari total **71,117 file gambar** yang diperiksa menggunakan `PIL.Image.verify()`:
* **Gambar Rusak (*Corrupted*):** **0 file** (100% gambar berformat JPEG/PNG valid dan dapat didekodekan).
* **Catatan Khusus Format:**
  * Dataset `Comparative Morphological and Phytochemical` berukuran **0 MB** (folder kosong).
  * Dataset `Leaf Image Dataset for Plant disease Classificatio` memuat **2 file arsip ZIP** berukuran 83,55 MB yang belum diekstrak.

---

## 3. Analisis Cakupan Penambahan Dataset Baru

Penambahan 9 folder dataset baru memberikan ekspansi signifikan terhadap kebutuhan aplikasi DaunKu:

1. **Tanaman Pekarangan & Sayuran (SRS Alignment):**
   * `Tomato leaf diseases` (2.627 gambar / 10 penyakit tomat): Menjawab kebutuhan eksplisit SRS DaunKu untuk tanaman tomat.
   * `Potato Leaf Disease Dataset` (3.076 gambar / 7 kelas penyakit kentang di lingkungan alami).
   * `A dataset of Yellow Disease in Horticultural Plant` (5.095 gambar deteksi penyakit kuning hortikultura).
2. **Tanaman Hias Bunga & Perkebunan:**
   * `Arabian Jasmine Leaf Condition Dataset (AJLCD-2025)` (6.315 gambar Melati dengan 8 kondisi daun).
   * `dataset for various disease detection of Rose,Tagetes erecta Hibiscusrosa-sinensis` (4.336 gambar Mawar, Marigold, dan Kembang Sepatu).
   * `Rubber_Leaf_Dataset` (3.481 gambar daun karet).
   * `Klasifikasi Penyakit Daun Kopi.v4i` (3.216 gambar daun kopi).
