# DaunKu AI — Rencana Implementasi Bertahap

**Dokumen kerja untuk Antigravity IDE**  
**Tanggal:** 23 November 2026  
**Status:** Rancangan awal. Semua angka dan dugaan dataset pada bagian inventaris awal harus diverifikasi dari file aktual sebelum dipakai untuk keputusan model atau training.

---

## 1. Tujuan proyek

Membangun komponen AI untuk aplikasi **DaunKu** yang nantinya dapat:

1. Mengenali jenis tanaman dari foto.
2. Mengidentifikasi kondisi atau gejala daun yang terlihat, sebatas kelas yang benar-benar didukung dataset.
3. Memberikan rekomendasi perawatan berdasarkan hasil identifikasi dan basis pengetahuan yang terpisah dari model.
4. Menyediakan API agar kelak dapat diintegrasikan dengan aplikasi DaunKu.

Pengerjaan harus bertahap. Prioritas pertama adalah memahami dataset dan menyiapkan fondasi proyek dengan aman, **bukan langsung melatih model**.

## 2. Kondisi lingkungan saat ini

Informasi lingkungan yang telah disampaikan pengguna:

- Sistem operasi: Windows.
- IDE: Antigravity IDE.
- Python terpasang: 3.13.9.
- RAM: 16 GB.
- GPU NVIDIA: tidak tersedia.
- Folder proyek AI: `IPPL/daunku_ai/`.
- Folder dataset: `IPPL/daunku_ai/Dataset/`.
- Aplikasi Flutter: `IPPL/daunku_app/`.

### Strategi komputasi

- Gunakan laptop untuk inspeksi dataset, skrip audit, preprocessing ringan, pengembangan API, dan eksperimen kecil.
- Jangan memuat seluruh dataset ke RAM sekaligus. Gunakan pemrosesan bertahap/batch.
- Training berat kemungkinan lebih sesuai dilakukan di Google Colab atau lingkungan cloud dengan GPU.
- Periksa kompatibilitas library dengan Python 3.13.9 sebelum memasang. Jika library penting belum kompatibel, buat environment terpisah dengan versi Python yang didukung; jangan mengubah instalasi Python global.
- Periksa ruang penyimpanan sebelum membuat salinan atau hasil preprocessing.

## 3. Inventaris dataset awal — WAJIB diverifikasi

Catatan berikut berasal dari pemeriksaan/perbincangan awal dan **belum boleh dianggap sebagai hasil audit final**. Antigravity harus memeriksa isi folder yang benar-benar tersedia dan memperbarui angka berdasarkan file aktual.

| Nama folder/dataset | Jenis yang dilaporkan | Jumlah awal yang dilaporkan | Catatan awal |
|---|---|---:|---|
| `goletplant.v5i.tensorflow` | Object detection | 26.063 gambar | Dilaporkan mencakup 52 spesies tanaman |
| `Houseplants Image Detection.v1i.tensorflow` | Object detection | 6.055 gambar | Diduga subset dari Goletplant |
| `Plant Classification and Disease.v1i.tensorflow` | Object detection | 628 gambar | Diduga subset dari versi v3 |
| `Plant Classification and Disease.v3i.tensorflow` | Object detection | 3.206 gambar | Dilaporkan memiliki 10 jenis tanaman dan 7 label kondisi |
| `Perfect Data Set` | Image classification | 3.449 gambar | Dilaporkan berisi Rose dan Marigold |
| `Rose And MArigold Leaf Disease 1` | Image classification | 3.449 gambar | Diduga duplikat dari Perfect Data Set |

**Jangan menjumlahkan angka di atas sebagai jumlah gambar unik.** Dataset dapat saling tumpang tindih, menjadi subset, atau mengandung duplikat. Audit harus membuktikannya.

### Label kondisi yang pernah teridentifikasi pada v3 — perlu verifikasi

- `Unhealthy-Sunburn`
- `Unhealthy-Rust`
- `Unhealthy-Leaf-Curl`
- `Unhealthy-Dehydration`
- `Unhealthy-Overwatering`
- `Unhealthy-Mineral-Deficiency`
- `Unhealthy-Powdery-Mildew`

### Jenis tanaman yang pernah teridentifikasi pada v3 — perlu verifikasi

- Aloe Vera
- Monstera Deliciosa
- Pothos / Epipremnum aureum
- Tradescantia zebrina
- Spider Plant
- Rubber Fig / Ficus elastica
- Snake Plant / Dracaena trifasciata
- Alocasia Frydek
- Aglaonema Commutatum
- Dracaena angolensis

### Label pada Perfect Data Set — perlu verifikasi

**Marigold**
- `Alternaria Leaf Blight`
- `Helathy Leaves` (kemungkinan salah eja pada sumber; jangan mengubah label asli tanpa mapping terdokumentasi)
- `Pest Damaged`

**Rose**
- `Botrytis blight`
- `Healthy`
- `Pest Damage`
- `Rose Mosaic Virus`

### Hal yang harus diperiksa

1. Apakah `Houseplants Image Detection` benar-benar subset Goletplant.
2. Apakah v1 benar-benar subset v3.
3. Apakah dua dataset Rose/Marigold berisi gambar yang sama.
4. Apakah split `train`, `valid`/`validation`, dan `test` tersedia serta konsisten.
5. Apakah ada anotasi kosong, label `-`, label tidak dikenal, atau gambar tanpa anotasi.
6. Apakah anotasi v3 menandai tanaman, gejala/kondisi, atau keduanya.
7. Apakah gambar Rose dan Marigold memiliki perbedaan latar yang dapat membuat model belajar latar, bukan ciri tanaman/penyakit.
8. Apakah ejaan label, kapitalisasi, dan nama spesies konsisten.

---

## 4. Aturan kerja wajib untuk Antigravity

1. **Dataset asli bersifat read-only.** Jangan menghapus, memindahkan, mengganti nama, mengedit, atau menimpa file apa pun di `Dataset/`.
2. Jangan melakukan training sebelum audit, pemetaan label, dan pembagian data selesai serta rancangan model disetujui pengguna.
3. Jangan mengubah folder `daunku_app/` atau kode Flutter pada tahap AI ini.
4. Jangan mengubah konfigurasi Supabase, kredensial, token, file `.env`, atau rahasia proyek.
5. Jangan melakukan commit, push, deployment, atau mengunggah dataset ke layanan eksternal tanpa persetujuan eksplisit.
6. Simpan hasil audit dan file turunan di luar folder dataset asli, misalnya `reports/`, `artifacts/`, atau `data_processed/`.
7. Sebelum menjalankan perintah yang menghapus atau menimpa file, berhenti dan minta persetujuan. Sebisa mungkin hindari operasi destruktif sepenuhnya.
8. Jangan mengarang hasil audit. Jika sesuatu tidak dapat diperiksa, tulis “belum diketahui”.
9. Berikan penjelasan dan ringkasan dalam Bahasa Indonesia yang sederhana.
10. Buat skrip yang dapat dijalankan ulang dan catat perintah yang digunakan.
11. Hindari membaca semua gambar ke memori sekaligus. Gunakan iterator, batch, atau sampling.
12. Jangan menganggap gambar tanpa label sebagai kelas `Healthy`. Label sehat hanya boleh diberikan jika sumber dataset memang menyatakannya.

---

## 5. Struktur folder proyek yang disarankan

Jangan memindahkan folder yang sudah ada. Buat struktur tambahan secara bertahap dan cek apakah nama folder sudah digunakan.

```text
IPPL/
├── daunku_ai/
│   ├── Dataset/                 # DATA ASLI — read-only
│   ├── .venv/                   # virtual environment lokal
│   ├── configs/                 # konfigurasi eksperimen
│   ├── data_processed/          # manifest atau data turunan bila diperlukan
│   ├── notebooks/               # eksplorasi dan eksperimen
│   ├── reports/                 # laporan audit dan evaluasi
│   ├── artifacts/               # hasil preprocessing dan artefak
│   ├── models/                  # checkpoint/model terlatih
│   ├── scripts/                 # skrip audit dan utilitas
│   ├── src/
│   │   └── daunku_ai/
│   │       ├── data/
│   │       ├── models/
│   │       ├── evaluation/
│   │       ├── inference/
│   │       └── api/
│   ├── tests/
│   ├── README.md
│   ├── requirements.txt
│   └── .gitignore
└── daunku_app/                  # aplikasi Flutter — jangan diubah sekarang
```

Jika struktur yang ada berbeda, pertahankan struktur saat ini dan usulkan perubahan terlebih dahulu. Jangan membuat folder duplikat tanpa alasan.

---

## 6. Roadmap pengerjaan

### Tahap 0 — Pemeriksaan proyek dan lingkungan

**Tujuan:** memahami kondisi folder dan menyiapkan lingkungan kerja yang aman.

Tugas:
- Periksa struktur `daunku_ai/` dan keberadaan `Dataset/`.
- Periksa apakah proyek menggunakan Git dan apakah ada perubahan lokal yang belum disimpan.
- Periksa versi Python, pip, arsitektur OS, ruang disk, dan environment Python yang sudah tersedia.
- Periksa `requirements.txt` atau `pyproject.toml` jika ada.
- Jangan memasang banyak library sekaligus sebelum kebutuhan dan kompatibilitas diketahui.
- Buat `.gitignore` hanya jika belum ada; jangan menimpa file yang sudah ada.
- Rekomendasikan versi Python dan environment virtual berdasarkan kompatibilitas aktual.

Output:
- `reports/environment_audit.md`
- Daftar struktur folder yang ditemukan.
- Rekomendasi environment dan dependensi minimum.

Kriteria selesai:
- Tidak ada file asli yang berubah.
- Versi Python dan kondisi lingkungan terdokumentasi.
- Kendala kompatibilitas dilaporkan.

### Tahap 1 — Inventaris dataset

**Tujuan:** mengetahui isi dataset secara faktual.

Tugas:
- Telusuri setiap folder dataset secara rekursif.
- Catat jumlah file berdasarkan ekstensi, ukuran total, ukuran per folder, dan jumlah gambar.
- Identifikasi struktur direktori seperti `train`, `valid`, `validation`, dan `test`.
- Identifikasi format anotasi: YOLO `.txt`, XML, JSON, CSV, atau format lain.
- Catat file konfigurasi dataset seperti `data.yaml`, README, atau metadata.
- Jangan mengasumsikan format hanya dari nama folder.

Output:
- `reports/dataset_inventory.md`
- `reports/dataset_inventory.csv`
- `artifacts/dataset_inventory.json`

Kriteria selesai:
- Semua folder dataset yang tersedia tercatat.
- Angka dihitung dari file aktual.
- File yang tidak dapat dibaca dicatat sebagai masalah.

### Tahap 2 — Audit label dan anotasi

**Tujuan:** memahami apa yang sebenarnya diajarkan oleh setiap dataset.

Tugas:
- Baca file konfigurasi dan anotasi.
- Identifikasi apakah dataset berupa klasifikasi gambar, object detection, atau gabungan.
- Catat seluruh nama kelas dan ID kelas.
- Hitung jumlah gambar dan anotasi per kelas, per split, dan per dataset.
- Periksa label di luar daftar kelas, anotasi kosong, koordinat bounding box tidak valid, dan gambar tanpa anotasi.
- Periksa apakah satu gambar dapat memiliki lebih dari satu objek atau label.
- Bedakan label spesies tanaman dengan label penyakit/gejala.
- Jangan menyamakan “tidak ada anotasi penyakit” dengan “tanaman sehat”.

Output:
- `reports/label_and_annotation_audit.md`
- `reports/class_distribution.csv`
- `reports/annotation_issues.csv`

Kriteria selesai:
- Daftar kelas sementara tersedia untuk setiap dataset.
- Format anotasi dan masalah kualitas terdokumentasi.
- Tidak ada label yang digabung atau diperbaiki tanpa catatan mapping.

### Tahap 3 — Audit duplikasi, subset, dan kebocoran data

**Tujuan:** mencegah gambar yang sama muncul di beberapa dataset atau split.

Tugas:
- Hitung hash kriptografis, misalnya SHA-256, untuk menemukan file identik.
- Jika sesuai, gunakan perceptual hash untuk menemukan gambar mirip yang diubah ukuran atau dikompresi.
- Bandingkan pasangan dataset yang diduga subset/duplikat.
- Periksa kemungkinan gambar identik tersebar di train, validation, dan test.
- Catat hasil; jangan menghapus file.
- Bedakan duplikat persis dan gambar yang hanya mirip.

Output:
- `reports/duplicate_audit.md`
- `reports/duplicate_groups.csv`
- `reports/potential_data_leakage.csv`

Kriteria selesai:
- Daftar kelompok duplikat dan tingkat keyakinannya tersedia.
- Ada rekomendasi dataset yang layak menjadi sumber utama.
- Tidak ada file yang dihapus atau dipindahkan.

### Tahap 4 — Pemeriksaan kualitas visual

**Tujuan:** memastikan gambar layak dipakai dan mencari potensi bias.

Tugas:
- Periksa gambar rusak/tidak dapat dibuka.
- Ringkas resolusi, rasio aspek, mode warna, dan ukuran file.
- Buat contact sheet dari sampel gambar per dataset dan kelas, bukan seluruh gambar sekaligus.
- Periksa ketidakseimbangan jumlah kelas.
- Periksa apakah latar, pencahayaan, sudut pengambilan, atau watermark terlalu berkaitan dengan kelas tertentu.
- Periksa apakah objek tanaman terlalu kecil/terpotong atau gejala tidak terlihat jelas.

Output:
- `reports/image_quality_audit.md`
- `reports/image_samples/` untuk contact sheet sampel.
- Daftar isu visual dan rekomendasi penanganan.

Kriteria selesai:
- Sampel tiap kelas utama sudah ditinjau.
- Bias yang mungkin memengaruhi model dicatat.
- Gambar asli tetap tidak berubah.

### Tahap 5 — Pemetaan label dan rancangan dataset kanonis

**Tujuan:** menyusun label konsisten tanpa menghilangkan label asli.

Tugas:
- Buat manifest berisi path gambar, dataset asal, split asal, label asli, label kanonis, dan informasi anotasi.
- Pisahkan `plant_species` (jenis tanaman) dari `plant_condition` atau `disease_or_symptom` (kondisi/gejala).
- Buat mapping nama sinonim hanya jika didukung bukti, dan simpan label asli.
- Tandai label ambigu atau tidak dapat dipetakan; jangan menebak.
- Tentukan apakah dataset tertentu hanya cocok untuk tugas tertentu.
- Hindari menggabungkan data klasifikasi dan deteksi menjadi satu format tanpa rancangan jelas.

Output:
- `configs/label_mapping.yaml`
- `artifacts/canonical_manifest.csv`
- `reports/canonical_dataset_design.md`

Kriteria selesai:
- Setiap label kanonis dapat dilacak ke asalnya.
- Label ambigu ditandai.
- Pengguna menyetujui pemetaan sebelum training.

### Tahap 6 — Pembagian train, validation, dan test

**Tujuan:** membuat evaluasi adil dan mencegah kebocoran data.

Tugas:
- Audit split bawaan dataset terlebih dahulu.
- Jika perlu membuat split baru, lakukan setelah duplikasi dan grup gambar diperiksa.
- Pembagian 80/10/10 hanya titik awal, bukan aturan otomatis.
- Gunakan stratifikasi bila sesuai dan memungkinkan.
- Pastikan gambar dari grup duplikat/seri foto yang sama tidak tersebar antar-split.
- Simpan test set sebagai data terkunci untuk evaluasi akhir.
- Catat seed, metode, dan daftar file setiap split.
- Jangan membuat validation/test terlalu kecil hanya demi mempertahankan persentase.

Output:
- `artifacts/splits/`
- `reports/data_split_plan.md`

Kriteria selesai:
- Tidak ada kebocoran duplikat yang diketahui antar-split.
- Distribusi kelas dan keterbatasannya dilaporkan.
- Split disetujui sebelum training.

### Tahap 7 — Rekomendasi arsitektur dan baseline

**Tujuan:** memilih pendekatan berdasarkan bentuk data dan kebutuhan aplikasi.

Evaluasi setidaknya opsi berikut:

1. **Pipeline dua tahap:** model identifikasi tanaman, lalu model kondisi/gejala yang relevan. Dipertimbangkan jika label spesies dan kondisi berasal dari sumber atau tugas berbeda.
2. **Object detection (misalnya keluarga YOLO):** dipertimbangkan jika bounding box konsisten dan aplikasi perlu menemukan lokasi daun/objek/gejala.
3. **Image classification:** dipertimbangkan jika satu gambar memiliki satu label utama dan tidak membutuhkan lokasi objek.
4. **Pendekatan gabungan:** hanya jika data dan kebutuhan produk mendukungnya.

Tugas:
- Bandingkan kualitas anotasi, jumlah data per kelas, variasi visual, kompleksitas, kebutuhan inferensi, dan keterbatasan hardware.
- Pilih baseline sederhana yang dapat diuji terlebih dahulu.
- Pertimbangkan transfer learning, bukan melatih model besar dari nol.
- Jelaskan trade-off akurasi, ukuran model, kecepatan, dan kemudahan deployment.
- Jangan memilih arsitektur hanya berdasarkan jumlah gambar atau popularitas framework.

Output:
- `reports/model_architecture_recommendation.md`
- Diagram alur pipeline.
- Rencana eksperimen baseline.

**TITIK PERSETUJUAN:** minta persetujuan pengguna sebelum training dimulai.

### Tahap 8 — Eksperimen training

Dilakukan hanya setelah persetujuan.

Tugas:
- Mulai dengan pilot kecil untuk memastikan pipeline data dan training berjalan.
- Gunakan pretrained model/transfer learning jika cocok.
- Catat konfigurasi, versi library, seed, dataset, dan checkpoint.
- Terapkan augmentasi hanya pada train set.
- Hindari augmentasi yang mengubah makna gejala atau membuat label tidak valid.
- Tangani ketidakseimbangan kelas dengan metode terukur.
- Pantau overfitting dan performa validation.
- Untuk training berat, siapkan notebook/skrip yang dapat dijalankan di Colab dengan dataset dan izin yang sesuai.
- Simpan checkpoint dan log eksperimen dengan nama jelas.

Output:
- Notebook atau skrip training.
- `reports/training_experiments/`
- `models/` untuk checkpoint.

### Tahap 9 — Evaluasi model

Untuk klasifikasi, laporkan:
- Accuracy.
- Precision, recall, dan F1 per kelas serta macro/weighted average.
- Confusion matrix.
- Contoh false positive dan false negative.
- Performa pada kelas dengan data sedikit.

Untuk object detection, laporkan:
- mAP dengan definisi threshold yang jelas.
- Precision dan recall.
- AP per kelas.
- Contoh bounding box yang salah atau terlewat.

Tambahan:
- Uji pada test set terkunci.
- Uji foto dengan kondisi berbeda dari dataset.
- Tentukan perilaku jika confidence rendah atau kelas tidak didukung.
- Jangan menyebut confidence sebagai probabilitas terkalibrasi kecuali kalibrasi telah diuji.
- Jangan menyatakan model dapat mendiagnosis semua penyakit tanaman.

Output:
- `reports/model_evaluation.md`
- Grafik dan confusion matrix.
- Rekomendasi kelayakan model.

### Tahap 10 — Basis pengetahuan rekomendasi perawatan

**Tujuan:** memisahkan prediksi visual dari saran perawatan.

Tugas:
- Susun basis pengetahuan terstruktur berdasarkan tanaman dan kondisi.
- Catat sumber tepercaya untuk setiap rekomendasi.
- Bedakan gejala visual, kemungkinan penyebab, dan tindakan perawatan.
- Sertakan peringatan bahwa gejala serupa dapat memiliki penyebab berbeda.
- Jangan memberi rekomendasi spesifik jika hasil model tidak cukup yakin atau tidak didukung basis pengetahuan.
- Sediakan respons “belum dapat diidentifikasi” untuk kondisi di luar cakupan.

Output:
- `configs/care_knowledge_base.yaml` atau format terstruktur lain.
- `reports/care_knowledge_sources.md`

### Tahap 11 — Pipeline inferensi

**Tujuan:** membuat alur prediksi konsisten dan mudah dipakai API.

Tugas:
- Tentukan validasi file gambar, ukuran, format, dan batas upload.
- Buat preprocessing yang sama dengan saat training.
- Susun hasil prediksi menjadi struktur data konsisten.
- Sertakan versi model, label, confidence/score, dan status cakupan.
- Tangani gambar tidak valid, tanaman tidak dikenal, dan confidence rendah.
- Jangan menyajikan satu prediksi sebagai diagnosis pasti.

Contoh skema respons awal (nilai berikut hanya contoh format, bukan hasil model nyata):

```json
{
  "status": "success",
  "model_version": "0.1.0",
  "plant": {
    "label": "Monstera Deliciosa",
    "score": 0.91
  },
  "condition": {
    "label": "Unhealthy-Sunburn",
    "score": 0.78
  },
  "recommendation_status": "available",
  "disclaimer": "Hasil merupakan estimasi berdasarkan ciri visual pada foto."
}
```

### Tahap 12 — API layanan AI

Dilakukan setelah pipeline inferensi stabil.

Tugas:
- Pertimbangkan FastAPI untuk layanan Python.
- Rancang endpoint:
  - `GET /health`
  - `GET /model-info`
  - `POST /predict`
- Validasi input, ukuran file, tipe MIME, dan error handling.
- Hindari menyimpan foto pengguna tanpa kebutuhan dan persetujuan jelas.
- Jangan menaruh secret atau credential di source code.
- Dokumentasikan cara menjalankan lokal dan konfigurasi deployment; jangan deploy tanpa izin.

Output:
- `src/daunku_ai/api/`
- Dokumentasi endpoint dan contoh request/response.
- Tes API.

### Tahap 13 — Integrasi dengan aplikasi Flutter

**Belum dikerjakan pada fase awal.** Mulai setelah model/API dan kontrak respons disetujui.

Sebelum mengubah aplikasi:
- Periksa struktur Flutter dan dokumentasi kebutuhan yang relevan.
- Tinjau SRS/SDD atau dokumen proyek jika tersedia.
- Usulkan titik integrasi dan perubahan file.
- Minta persetujuan pengguna sebelum mengedit `daunku_app/`.
- Jangan mengubah alur aplikasi tanpa memahami dampaknya.

Output:
- Dokumen kontrak integrasi.
- Rencana perubahan file Flutter.
- Integrasi dan pengujian setelah persetujuan.

### Tahap 14 — Dokumentasi dan serah terima

Tugas:
- Perbarui `README.md`.
- Dokumentasikan setup environment, audit data, training, evaluasi, inferensi, dan API.
- Buat model card: tujuan, data, kelas yang didukung, keterbatasan, metrik, dan risiko.
- Catat versi dataset dan model.
- Sediakan instruksi reproduksi eksperimen.

Output:
- Dokumentasi teknis.
- Model card.
- Panduan menjalankan proyek dari awal.

---

## 7. Batas kemampuan dan kehati-hatian

- Dataset yang tersedia belum tentu mencakup semua tanaman yang mungkin diminta pengguna.
- Jika dataset hanya mencakup tanaman tertentu, model tidak boleh mengaku dapat mengenali tanaman di luar kelas tersebut.
- Dataset yang disebutkan sejauh ini belum membuktikan dukungan untuk diagnosis Mangga, Jambu, Cabai, atau Tomat. Jangan menambahkan kelas tersebut tanpa data berlabel yang sesuai.
- Gejala visual tidak selalu cukup untuk memastikan penyakit biologis tertentu. Gunakan istilah “indikasi” atau “kemungkinan kondisi” bila sesuai.
- Kelas `Healthy` harus berasal dari anotasi/label sehat yang eksplisit, bukan asumsi dari ketiadaan label.
- Data yang banyak belum tentu berkualitas; kualitas anotasi, keragaman, dan pemisahan data sama pentingnya.
- Jangan menggabungkan dataset duplikat atau subset secara naif karena dapat membuat metrik evaluasi tampak lebih baik daripada kemampuan sebenarnya.

## 8. Kriteria keberhasilan proyek

Proyek dianggap siap masuk tahap integrasi jika:

1. Dataset dan label telah diaudit serta dapat dilacak ke sumbernya.
2. Duplikasi dan kebocoran data telah diperiksa.
3. Split train/validation/test terdokumentasi.
4. Arsitektur dipilih berdasarkan bukti dan disetujui.
5. Evaluasi per kelas tersedia, bukan hanya satu angka accuracy.
6. Batas kelas yang didukung dan perilaku confidence rendah jelas.
7. Rekomendasi perawatan memiliki sumber dan tidak dibuat-buat.
8. Pipeline inferensi memiliki kontrak input/output yang stabil.
9. API telah diuji.
10. Integrasi Flutter dilakukan dengan persetujuan dan dokumentasi.

---

## 9. Instruksi tugas pertama untuk Antigravity

**Kerjakan hanya Tahap 0, Tahap 1, dan Tahap 2. Setelah itu berhenti dan laporkan hasilnya.**

Instruksi operasional:

1. Baca dokumen ini terlebih dahulu.
2. Periksa `IPPL/daunku_ai/` dan `Dataset/` secara read-only.
3. Jangan mengubah aplikasi Flutter.
4. Jangan melakukan training model.
5. Jangan menghapus, memindahkan, mengganti nama, atau menimpa dataset.
6. Buat skrip audit yang aman dan dapat dijalankan ulang.
7. Jalankan audit dengan pemrosesan bertahap agar RAM 16 GB cukup.
8. Simpan laporan di `reports/` dan ringkasan data di `artifacts/`.
9. Jika folder output sudah ada, jangan menimpa file tanpa membuat nama baru atau meminta persetujuan.
10. Catat kendala Python 3.13.9 dan jangan memasang dependency besar tanpa memeriksa kompatibilitas.
11. Jangan melanjutkan ke Tahap 3 atau tahap berikutnya sebelum melaporkan hasil Tahap 0–2.

### Format laporan yang harus diberikan Antigravity

- Ringkasan kondisi proyek.
- Versi Python dan rekomendasi environment.
- Daftar dataset yang benar-benar ditemukan.
- Jumlah file/gambar aktual per dataset dan split.
- Format anotasi yang ditemukan.
- Daftar seluruh kelas beserta jumlah sampel jika dapat dihitung.
- File rusak, anotasi kosong, label tidak dikenal, atau masalah lain.
- Perbedaan hasil aktual dengan inventaris awal dokumen ini.
- Daftar pertanyaan/keputusan yang membutuhkan persetujuan pengguna.
- Konfirmasi bahwa dataset asli dan aplikasi Flutter tidak diubah.

**Akhiri pekerjaan setelah laporan Tahap 0–2 selesai. Jangan mulai training.**
