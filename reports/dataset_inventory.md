# Laporan Inventaris Dataset Aktual (Tahap 1) — DaunKu AI

> **Waktu Audit:** 23 November 2026  
> **Status:** Selesai  
> **Metode:** Penelusuran rekursif file aktual & validasi integritas biner gambar (streaming PIL).

---

## 1. Ringkasan Inventaris Aktual Dataset

Berdasarkan pembacaan biner dan direktori langsung di folder `daunku_ai/Dataset/`, ditemukan **6 folder dataset** dengan rincian aktual sebagai berikut:

| No | Nama Dataset | Tipe Task | Format Anotasi | Total Gambar | Train | Valid | Test | Unsplit | Ukuran (MB) |
| :-: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `Houseplants Image Detection.v1i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **6,055** | 5,967 | 4 | 84 | 0 | 320.69 MB |
| 2 | `Perfect Data Set` | Image Classification | Directory Structure (Folder per Class) | **3,449** | 0 | 0 | 0 | 3,449 | 1,649.84 MB |
| 3 | `Plant Classification and Disease.v1i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **628** | 563 | 46 | 19 | 0 | 33.65 MB |
| 4 | `Plant Classification and Disease.v3i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **3,184** | 2,921 | 178 | 85 | 0 | 222.62 MB |
| 5 | `Rose And MArigold Leaf Disease 1` | Image Classification | Directory Structure (Folder per Class) | **3,449** | 0 | 0 | 0 | 3,449 | 1,649.84 MB |
| 6 | `goletplant.v5i.tensorflow` | Object Detection | TensorFlow Object Detection (_annotations.csv) | **26,063** | 25,373 | 22 | 668 | 0 | 4,919.25 MB |
| | **TOTAL KESELURUHAN (Mentah)** | | | **42,828** | | | | | **8.59 GB** |

> [!IMPORTANT]
> **Peringatan Integritas:** Angka total di atas (42,828 gambar) adalah jumlah file mentah di disk sebelum deduping. Nilai ini mengandung duplikasi dan subset identik yang signifikan:
> 1. `Rose And MArigold Leaf Disease 1` (3,449 gambar) adalah duplikat persis 100% dari `Perfect Data Set`.
> 2. `Houseplants Image Detection` (6,055 gambar) adalah subset murni dari `goletplant.v5i`.
> 3. `Plant Classification and Disease v1` (628 gambar) adalah subset murni dari `v3`.

---

## 2. Pemeriksaan File Rusak (*Corrupted Files*)

Seluruh 42,828 file gambar telah diverifikasi secara biner menggunakan header validation (`PIL.Image.verify()`):
* **Jumlah gambar rusak / gagal dibaca:** **0 file** (100% gambar berformat JPEG valid dan dapat dibuka).

---

## 3. Rincian Konfigurasi & Metadata per Dataset

### A. `Houseplants Image Detection.v1i.tensorflow`
* **Tipe Tugas:** Object Detection
* **Format Anotasi:** TensorFlow Object Detection (_annotations.csv)
* **Total Gambar:** 6,055 gambar
* **Distribusi Ekstensi:** {'.txt': 2, '.jpg': 6055, '.csv': 3}
* **Pembagian Split:**
  * `root`: 0 gambar, 0 file anotasi
  * `test`: 84 gambar, 1 file anotasi
  * `train`: 5,967 gambar, 1 file anotasi
  * `valid`: 4 gambar, 1 file anotasi
* **File Metadata / Config:** `README.dataset.txt, README.roboflow.txt`

### A. `Perfect Data Set`
* **Tipe Tugas:** Image Classification
* **Format Anotasi:** Directory Structure (Folder per Class)
* **Total Gambar:** 3,449 gambar
* **Distribusi Ekstensi:** {'.jpg': 3449}
* **Pembagian Split:**
  * `subfolders`: 3,449 gambar, 0 file anotasi
* **File Metadata / Config:** `None`

### A. `Plant Classification and Disease.v1i.tensorflow`
* **Tipe Tugas:** Object Detection
* **Format Anotasi:** TensorFlow Object Detection (_annotations.csv)
* **Total Gambar:** 628 gambar
* **Distribusi Ekstensi:** {'.txt': 2, '.jpg': 628, '.csv': 3}
* **Pembagian Split:**
  * `root`: 0 gambar, 0 file anotasi
  * `test`: 19 gambar, 1 file anotasi
  * `train`: 563 gambar, 1 file anotasi
  * `valid`: 46 gambar, 1 file anotasi
* **File Metadata / Config:** `README.dataset.txt, README.roboflow.txt`

### A. `Plant Classification and Disease.v3i.tensorflow`
* **Tipe Tugas:** Object Detection
* **Format Anotasi:** TensorFlow Object Detection (_annotations.csv)
* **Total Gambar:** 3,184 gambar
* **Distribusi Ekstensi:** {'.txt': 2, '.jpg': 3184, '.csv': 3}
* **Pembagian Split:**
  * `root`: 0 gambar, 0 file anotasi
  * `test`: 85 gambar, 1 file anotasi
  * `train`: 2,921 gambar, 1 file anotasi
  * `valid`: 178 gambar, 1 file anotasi
* **File Metadata / Config:** `README.dataset.txt, README.roboflow.txt`

### A. `Rose And MArigold Leaf Disease 1`
* **Tipe Tugas:** Image Classification
* **Format Anotasi:** Directory Structure (Folder per Class)
* **Total Gambar:** 3,449 gambar
* **Distribusi Ekstensi:** {'.jpg': 3449}
* **Pembagian Split:**
  * `subfolders`: 3,449 gambar, 0 file anotasi
* **File Metadata / Config:** `None`

### A. `goletplant.v5i.tensorflow`
* **Tipe Tugas:** Object Detection
* **Format Anotasi:** TensorFlow Object Detection (_annotations.csv)
* **Total Gambar:** 26,063 gambar
* **Distribusi Ekstensi:** {'.txt': 2, '.jpg': 26063, '.csv': 3}
* **Pembagian Split:**
  * `root`: 0 gambar, 0 file anotasi
  * `test`: 668 gambar, 1 file anotasi
  * `train`: 25,373 gambar, 1 file anotasi
  * `valid`: 22 gambar, 1 file anotasi
* **File Metadata / Config:** `README.dataset.txt, README.roboflow.txt`

