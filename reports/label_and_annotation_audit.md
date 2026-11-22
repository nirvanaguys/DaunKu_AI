# Laporan Audit Label dan Anotasi (Tahap 2) — DaunKu AI

> **Waktu Audit:** 23 November 2026  
> **Status:** Selesai  
> **Dokumen Acuan:** `Rencana_Implementasi_AI_DaunKu.md`  
> **Sumber Analisis:** Pemeriksaan seluruh baris anotasi CSV dan struktur folder kelas secara aktual.

---

## 1. Ringkasan Temuan Audit Label

Audit menganalisis **seluruh 67.249 baris anotasi bounding box** pada 4 dataset Object Detection serta struktur folder pada 2 dataset klasifikasi:

1. **Pemisahan Peran Dataset:**
   * `goletplant.v5i` murni berisi **52 spesies tanaman hias** (41.587 bounding box). Tidak ada label penyakit sama sekali.
   * `Plant Classification and Disease.v3i` menggabungkan **10 spesies tanaman hias** (7.867 box) dan **7 label gejala/penyakit** (2.439 box) dalam satu file anotasi.
   * `Perfect Data Set` fokus pada klasifikasi daun **Mawar (4 kondisi)** dan **Marigold (3 kondisi)**.
2. **Kondisi Anotasi Kotor / Rusak:**
   * Terdeteksi **857 total anomali/catatan kualitas** yang telah dicatat lengkap di `reports/annotation_issues.csv`.

### Rangkuman Masalah Anotasi yang Ditemukan:
| Tipe Masalah | Jumlah Kejadian | Dampak & Penjelasan |
| :--- | :---: | :--- |
| **Label Kotor / Placeholder (`-`)** | 3 baris | Ditemukan label tanda minus `-` pada dataset `goletplant` train (3 box). Wajib dibersihkan. |
| **Typo Nama Kelas** | 2 direktori | Direktori `Helathy Leaves` di Marigold (salah eja dari `Healthy Leaves`). |
| **Koordinat Bounding Box Out-of-Bounds** | 436 box | Koordinat `xmax` atau `ymax` melebihi resolusi kanvas gambar. |
| **Koordinat Negatif / Tidak Valid** | 0 box | Koordinat dengan nilai negatif atau lebar nol/terbalik. |
| **Bias Latar Belakang Terpotong (*no_bg*)** | 8 kelas | Seluruh 2.760 gambar Mawar menggunakan foto daun tanpa latar belakang (*segmented/no_bg*). |

---

## 2. Taksonomi Kelas Aktual: `Plant Classification and Disease.v3i` (Train Split)

Dataset ini merupakan kandidat utama untuk diagnosis daun tanaman hias DaunKu:

### A. Kelas Spesies Tanaman (10 Kelas):
| Nama Kelas di Anotasi | Nama Umum / Taksonomi | Bounding Box | Gambar Unik |
| :--- | :--- | :---: | :---: |
| `Aloe-Vera-Aloe-barbadensis-` | Aloe Vera Aloe barbadensis | 1,985 | 461 |
| `Swiss Cheese Plant -Monstera Deliciosa-` | Swiss Cheese Plant  Monstera Deliciosa | 1,328 | 552 |
| `Pothos-Epipremnum-aureum-` | Pothos Epipremnum aureum | 917 | 234 |
| `Inch-Plant-Tradescantia-zebrina-` | Inch Plant Tradescantia zebrina | 915 | 102 |
| `Spider-Plant-Chloropythum-Comosum-` | Spider Plant Chloropythum Comosum | 888 | 470 |
| `Rubber-Fig-Ficus-Elastica-` | Rubber Fig Ficus Elastica | 686 | 107 |
| `Snake-Plant-Dracaena-trifasciata-` | Snake Plant Dracaena trifasciata | 671 | 224 |
| `Alocasia-Green-Velvet-Micholitziana-Frydek-` | Alocasia Green Velvet Micholitziana Frydek | 392 | 129 |
| `Philippine-Evergreen-Aglaonema-Commutatum-` | Philippine Evergreen Aglaonema Commutatum | 327 | 86 |
| `Spear-Plant-Dracaena-angolensis-` | Spear Plant Dracaena angolensis | 158 | 47 |

### B. Kelas Gejala / Penyakit Tanaman (7 Kelas):
| Nama Kelas di Anotasi | Deskripsi Gejala / Masalah | Bounding Box | Gambar Unik |
| :--- | :--- | :---: | :---: |
| `Unhealthy-Sunburn` | Daun terbakar sinar matahari berlebih | 605 | 299 |
| `Unhealthy-Rust` | Karat daun (infeksi jamur) | 460 | 140 |
| `Unhealthy-Leaf-Curl` | Daun menggulung / distorsi | 380 | 126 |
| `Unhealthy-Dehydration` | Kurang air / daun layu mengering | 321 | 156 |
| `Unhealthy-Overwatering` | Kelebihan air / busuk akar | 117 | 66 |
| `Unhealthy-Mineral-Deficiency` | Defisiensi hara / klorosis | 87 | 57 |
| `Unhealthy-Powdery-Mildew` | Embun tepung (infeksi jamur) | 69 | 63 |

> [!NOTE]
> **Karakteristik Multi-Label:** Terdapat **622 gambar** pada train set v3 yang memiliki anotasi tanaman sekaligus anotasi gejala daun pada satu gambar yang sama (misal: daun *Rubber Fig* dengan kotak *Sunburn*).

---

## 3. Taksonomi Kelas Aktual: `Perfect Data Set` (Mawar & Marigold)

| Tanaman | Label Kondisi Aktual | Jumlah Gambar Aktual | Catatan Kualitas Latar Belakang |
| :--- | :--- | :---: | :--- |
| **Marigold** | `Alternaria Leaf Blight` | 338 gambar | Natural background (asli di kebun/pot) |
| **Marigold** | `Helathy Leaves` *(typo)* | 273 gambar | Natural background (sehat) |
| **Marigold** | `Pest Damaged` | 78 gambar | Natural background (rusak hama) |
| **Rose** | `botrytis blight` | 558 gambar | ⚠️ **100% no_bg_*** (latar belakang dihapus) |
| **Rose** | `Healthy` | 1.167 gambar | ⚠️ **100% no_bg_*** (latar belakang dihapus) |
| **Rose** | `Pest Damage` | 790 gambar | ⚠️ **100% no_bg_*** (latar belakang dihapus) |
| **Rose** | `Rose Mosaic Virus` | 245 gambar | ⚠️ **100% no_bg_*** (latar belakang dihapus) |

---

## 4. Evaluasi terhadap Kebutuhan DaunKu (SRS Alignment)

1. **Kesesuaian Tanaman Hias:** Sangat kuat pada 10 tanaman hias utama di v3i dan 52 tanaman di Goletplant.
2. **Kesesuaian Masalah Perawatan:** Gejala *sunburn, overwatering, dehydration, rust* sangat aplikatif untuk target pengguna aplikasi DaunKu.
3. **Ketiadaan Tanaman Pekarangan:** Tidak ada satupun gambar cabai, tomat, mangga, atau jambu di seluruh 6 dataset yang diaudit.
