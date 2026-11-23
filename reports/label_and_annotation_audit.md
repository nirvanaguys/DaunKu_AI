# Laporan Audit Label dan Anotasi (Tahap 2 — 15 Dataset) — DaunKu AI

> **Waktu Audit:** 23 November 2026 (Pembaruan Pasca Penambahan Dataset)  
> **Status:** Selesai  
> **Dokumen Acuan:** `Rencana_Implementasi_AI_DaunKu.md`  
> **Cakupan Analisis:** Pemeriksaan seluruh baris anotasi CSV, file teks YOLO, dan struktur direktori kelas pada 15 dataset.

---

## 1. Ringkasan Temuan Audit Kualitas Anotasi

Total terdeteksi **944 catatan kualitas/anomali** di seluruh dataset:

| Tipe Masalah / Anomali | Jumlah Kejadian | Penjelasan & Dampak |
| :--- | :---: | :--- |
| **Koordinat Bounding Box Melebihi Batas Kanvas** | 436 | Koordinat `xmax > width` atau `ymax > height` akibat pembulatan augmentasi Roboflow / YOLO. |
| **Gambar Yatim (*Orphaned Images*)** | 485 | Gambar yang ada di disk tetapi tidak tercatat di file anotasi (354 di v3i, 54 di goletplant). |
| **Dataset Kopi Hanya Memiliki Label `'leaf'`** | 1 dataset | Dataset `Klasifikasi Penyakit Daun Kopi` hanya memiliki label kelas `'leaf'` (lokalisasi daun saja, **tanpa label penyakit sama sekali**). |
| **Metadata Nama Kelas Hilang** | 1 dataset | Dataset `Yellow Disease` menggunakan label numerik `0` dan `1` tanpa file mapping nama kelas (*data.yaml* tidak ada). |
| **Dataset Kosong / Belum Diekstrak** | 0 dataset | Folder kosong (`Comparative...`) dan arsip ZIP belum diekstrak (`Leaf Image...`). |
| **Typo pada Nama Kelas Folder** | 4 direktori | `Helathy Leaves` (Marigold), `Heaalthy Leaf` (Tagetes), `Cholorosis` (Jasmine). |
| **Bias Latar Belakang Dihapus (*no_bg*)** | 14 kelas | Seluruh foto Mawar menggunakan daun berlatar belakang terpotong sintetis. |
| **Redundansi Raw vs Compressed** | 1 dataset | `Rubber_Leaf_Dataset` menyalin seluruh data dua kali (`Compressed_Dataset` dan `Raw_Dataset`). |

---

## 2. Taksonomi Kelas Baru yang Signifikan

### A. Penyakit Daun Tomat (`Tomato leaf diseases` — 2.627 gambar):
* `Leaf Miner` (519 gambar) — ulat penggorok daun
* `Tomato Leaf Curl Virus` (394 gambar) — virus daun keriting
* `Bacterial Spot` (376 gambar) — bercak bakteri
* `Insect Damage` (336 gambar) — gigitan serangga
* `Spider Mites` (307 gambar) — tungau merah
* `Early Blight` (204 gambar) — hawar daun dini
* `Late Blight` (166 gambar) — hawar daun lanjut
* `Cercospora leaf mold` (156 gambar) — kapang cercospora
* `Healthy` (103 gambar) — daun tomat sehat
* `Leaf Mold` (66 gambar) — kapang daun

### B. Penyakit Daun Melati (`Arabian Jasmine (AJLCD-2025)` — 6.315 gambar):
* `Healthy` (955)
* `Dried Leaf` (916)
* `Leaf Blight` (778)
* `Pest Damage` (754)
* `Anthracnose` (754)
* `Leaf Spot` (733)
* `Initial stage` (726)
* `Cholorosis` [sic] (699)

### C. Penyakit Daun Kentang (`Potato Leaf Disease` — 3.076 gambar):
* `Fungi` (748), `Pest` (611), `Bacteria` (569), `Virus` (532), `Phytopthora` (347), `Healthy` (201), `Nematode` (68).
