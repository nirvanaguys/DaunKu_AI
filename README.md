# DaunKu AI — Komponen Kecerdasan Buatan Aplikasi DaunKu

Repositori ini memuat rancangan, skrip audit, eksperimen, basis pengetahuan rekomendasi perawatan, dan layanan API untuk komponen **Artificial Intelligence (AI)** pada aplikasi **DaunKu**.

DaunKu adalah aplikasi mobile untuk membantu pengguna merawat tanaman melalui diagnosis tanaman berbasis foto, rekomendasi perawatan, dan marketplace perlengkapan berkebun.

---

## 📁 Struktur Repositori

```text
daunku_ai/
├── artifacts/                # Artefak terstruktur (JSON inventaris, manifest kanonis, split)
├── configs/                  # Konfigurasi label mapping & knowledge base
├── reports/                  # Laporan audit dataset, analisis kualitas, dan evaluasi
├── scripts/                  # Skrip Python mandiri untuk audit, preprocessing, dan utilitas
├── src/                      # Source code modul AI DaunKu & API FastAPI
├── .gitignore                # Pengecualian dataset mentah, virtualenv, dan checkpoint
├── DaunKu_Analisis_Dataset_dan_Rancangan_AI.md  # Dokumen analisis awal dataset
├── Rencana_Implementasi_AI_DaunKu.md           # Pedoman dan roadmap implementasi bertahap
└── README.md                 # Dokumentasi repositori
```

> **Catatan Pengelolaan Data:** Dataset mentah (~19,2 GB / 85.022 gambar) dikelola secara lokal pada direktori `Dataset/` dalam kondisi *read-only* dan dikecualikan dari pelacakan Git melalui `.gitignore`.

---

## 📊 Ringkasan Koleksi Dataset (Status Audit Aktual)

Berdasarkan audit rekursif dan validasi biner berekstensi JPEG/PNG menggunakan Pillow, seluruh **85.022 gambar** berada dalam kondisi valid (**0 file rusak / zero corruption**), terbagi ke dalam **14 folder dataset**:

| No | Nama Dataset | Tipe Tugas | Format Anotasi | Total Gambar | Cakupan / Komoditas |
| :-: | :--- | :--- | :--- | :---: | :--- |
| **1** | `goletplant.v5i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 26.063 | 52 varietas tanaman hias populer |
| **2** | `Leaf Image Dataset for Plant disease Classificatio` | Klasifikasi | Folder per Kelas | 13.905 | 7 tanaman sayuran pekarangan & 58 kelas penyakit |
| **3** | `Arabian Jasmine Leaf Condition Dataset (AJLCD-2025` | Klasifikasi | Folder per Kelas | 6.315 | Bunga Melati (*8 kondisi kesehatan*) |
| **4** | `Houseplants Image Detection.v1i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 6.055 | 24 tanaman hias (*subset murni goletplant*) |
| **5** | `A dataset of Yellow Disease in Horticultural Plant` | Deteksi Objek | YOLO Darknet (`.txt`) | 5.095 | Penyakit kuning tanaman hortikultura |
| **6** | `dataset for various disease detection of Rose,Tagetes,Hibiscus` | Klasifikasi | Folder per Kelas | 4.479 | Mawar, Marigold, dan Kembang Sepatu |
| **7** | `Rubber_Leaf_Dataset` | Klasifikasi | Folder per Kelas | 3.481 | Daun Karet (*4 kondisi penyakit*) |
| **8** | `Perfect Data Set` | Klasifikasi | Folder per Kelas | 3.449 | Daun Mawar & Marigold (*subset induk No. 6*) |
| **9** | `Rose And MArigold Leaf Disease 1` | Klasifikasi | Folder per Kelas | 3.449 | *Duplikat persis 100% dari No. 8* |
| **10** | `Klasifikasi Penyakit Daun Kopi.v4i.tensorflow` | Deteksi Objek | TF CSV | 3.216 | Daun Kopi (*label anotasi murni 'leaf'*) |
| **11** | `Plant Classification and Disease.v3i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 3.184 | 10 tanaman hias + 7 masalah perawatan daun |
| **12** | `Potato Leaf Disease Dataset in Uncontrolled Environment` | Klasifikasi | Folder per Kelas | 3.076 | Daun Kentang (*7 kelas patogen di kebun nyata*) |
| **13** | `Tomato leaf diseases` | Klasifikasi | Folder per Kelas | 2.627 | Daun Tomat (*10 penyakit sesuai SRS DaunKu*) |
| **14** | `Plant Classification and Disease.v1i.tensorflow` | Deteksi Objek | TF CSV Bounding Box | 628 | *Subset murni dari v3i* |
| | **TOTAL KESELURUHAN (Mentah)** | | | **85.022** | **Kapasitas Disk: ~19,2 GB** |

---

## 🚀 Status Roadmap Pengembangan AI

Mengacu pada dokumen kerja [Rencana_Implementasi_AI_DaunKu.md](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/Rencana_Implementasi_AI_DaunKu.md):

* [x] **Tahap 0 — Pemeriksaan Lingkungan:** Verifikasi Python 3.13.9, ketersediaan library data science, dan hardware (`reports/environment_audit.md`).
* [x] **Tahap 1 — Inventarisasi Dataset:** Menelusuri seluruh 14 dataset, 85.022 file gambar, dan split data (`reports/dataset_inventory.md` & `artifacts/dataset_inventory.json`).
* [x] **Tahap 2 — Audit Label & Anotasi:** Menganalisis taksonomi kelas tanaman hias, sayuran, bunga, dan perkebunan serta mencatat 944 anomali/catatan kualitas (`reports/label_and_annotation_audit.md` & `reports/annotation_issues.csv`).
* [ ] **Tahap 3 — Audit Duplikasi & Kebocoran Data:** Kalkulasi sidik jari hash (SHA-256) untuk mendeteksi gambar duplikat/subset identik.
* [ ] **Tahap 4 — Pemeriksaan Kualitas Visual:** Peninjauan sampel gambar per kelas, mendeteksi bias latar belakang (*no_bg bias*).
* [ ] **Tahap 5 — Pemetaan Label & Manifest Kanonis:** Menyusun *canonical dataset* terpadu untuk kebutuhan model DaunKu.
* [ ] **Tahap 6 — Pembagian Data (Stratified Re-Split):** Membagi dataset ke dalam 80% Train, 10% Valid, dan 10% Test secara seimbang.
* [ ] **Tahap 7–12 — Pemodelan AI, Evaluasi, Knowledge Base & API FastAPI:** Melatih model klasifikasi/deteksi, menyusun basis rekomendasi perawatan, dan membangun REST API inferensi.
* [ ] **Tahap 13–14 — Integrasi Aplikasi Flutter & Dokumentasi Final.**

---

## 🛠️ Menjalankan Skrip Audit Mandiri

Untuk mereproduksi audit integritas dataset, verifikasi biner gambar, dan pemeriksaan anotasi secara lokal:

```bash
python scripts/run_audit_stage0_to_2.py
```

Laporan hasil audit akan otomatis diperbarui pada folder `reports/` dan `artifacts/`.
