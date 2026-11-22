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
├── .gitignore                # Pengecualian dataset besar, virtualenv, dan checkpoint
├── DaunKu_Analisis_Dataset_dan_Rancangan_AI.md  # Dokumen analisis awal dataset
├── Rencana_Implementasi_AI_DaunKu.md           # Pedoman dan roadmap implementasi bertahap
└── README.md                 # Dokumentasi repositori
```

> **Catatan Dataset:** Dataset mentah (~8,8 GB) dikelola secara lokal pada direktori `Dataset/` dan dikecualikan dari Git tracking melalui `.gitignore`.

---

## 🚀 Status Pengembangan Terkini

* [x] **Tahap 0 — Pemeriksaan Lingkungan:** Konfigurasi Python 3.13 dan spesifikasi hardware terdokumentasi di `reports/environment_audit.md`.
* [x] **Tahap 1 — Inventaris Dataset:** Seluruh 42.828 file gambar pada 6 dataset telah diverifikasi integritasnya tanpa file rusak (`reports/dataset_inventory.md`).
* [x] **Tahap 2 — Audit Label & Anotasi:** Analisis 67.249 baris bounding box dan taksonomi kelas (`reports/label_and_annotation_audit.md`).
* [ ] **Tahap 3 — Audit Duplikasi & Kebocoran Data**
* [ ] **Tahap 4 — Pemeriksaan Kualitas Visual**
* [ ] **Tahap 5 — Pemetaan Label & Manifest Kanonis**
* [ ] **Tahap 6 — Pembagian Data (Stratified Split)**
* [ ] **Tahap 7 s/d 12 — Pemodelan, Knowledge Base & API Service**

---

## 🛠️ Menjalankan Skrip Audit

Untuk menjalankan audit dataset dan label secara lokal:

```bash
python scripts/run_audit_stage0_to_2.py
```
