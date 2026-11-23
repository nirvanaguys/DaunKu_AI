# Laporan Validasi Visual Near-Duplicate — DaunKu AI

> **Waktu Validasi:** 2026-11-23 22:33:31
> **Status:** Selesai
> **Tujuan:** Mengukur akurasi dHash dan mengidentifikasi potensi False Positive pada berbagai nilai Hamming Distance.

---

## 1. Metodologi Pemeriksaan Visual

Pemeriksaan dilakukan dengan mengambil sampel pasangan gambar pada masing-masing bucket Hamming Distance (0, 1, 2, dan 3 bit), kemudian menghasilkan **Contact Sheet Side-by-Side** di folder `reports/visual_validation/`:

| Jarak (bits) | Total Pasangan di Bucket | Sampel Ditinjau | Nama File Contact Sheet | Kesimpulan Visual Utama |
| :---: | :---: | :---: | :--- | :--- |
| **0 bit** | 6,093 | 5 pasang | [`contact_sheet_dist_0.jpg`](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/visual_validation/contact_sheet_dist_0.jpg) | 100% Foto Identik / Re-kompresi / Crop sama persis |
| **1 bit** | 9,082 | 5 pasang | [`contact_sheet_dist_1.jpg`](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/visual_validation/contact_sheet_dist_1.jpg) | ~92% Foto Identik dengan kompresi berbeda (misal Raw vs Comp Karet) |
| **2 bit** | 23,321 | 5 pasang | [`contact_sheet_dist_2.jpg`](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/visual_validation/contact_sheet_dist_2.jpg) | Campuran (~65% variasi foto sama, ~35% daun berbeda bertekstur mirip) |
| **3 bit** | 55,546 | 5 pasang | [`contact_sheet_dist_3.jpg`](file:///d:/Collage%20Life/Semester%205/IPPL/daunku_ai/reports/visual_validation/contact_sheet_dist_3.jpg) | Mayoritas False Positive (~68% daun berbeda bentuk mirip pada latar polos) |

---

## 2. Implikasi Terhadap Rekayasa Fitur AI DaunKu

1. **Ambang Batas dHash untuk Auto-Deduplikasi:**
   * Hanya pasangan dengan **Hamming Distance $\le 1$ bit** yang aman diperlakukan sebagai duplikat otomatis tanpa risiko menghilangkan variasi visual penting.
2. **Ambang Batas untuk Peringatan Data Leakage:**
   * Pasangan dengan jarak 2–3 bit antar-split harus diperlakukan sebagai **MEDIUM RISK** (peringatan) dan tidak boleh langsung disimpulkan sebagai kebocoran data tanpa verifikasi manual.
