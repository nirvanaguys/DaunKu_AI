# Laporan Audit Lingkungan (Tahap 0) — DaunKu AI

> **Waktu Audit:** 23 November 2026  
> **Status:** Selesai  
> **Dokumen Acuan:** `Rencana_Implementasi_AI_DaunKu.md`

---

## 1. Spesifikasi Perangkat Keras dan Sistem Operasi

| Komponen | Spesifikasi Aktual | Catatan |
| :--- | :--- | :--- |
| **Sistem Operasi** | Windows 11 (64bit) | Windows 64-bit |
| **Arsitektur CPU** | AMD64 (AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD) | CPU Intel/AMD x86_64 |
| **Kapasitas RAM** | 16 GB | Sesuai konteks laptop pengguna |
| **GPU Terakselerasi** | Tidak tersedia (CPU Only) | Training berat diarahkan ke Colab/Cloud |
| **Kapasitas Disk (Drive D:)** | Total: 234.37 GB \| Terpakai: 120.8 GB \| **Tersedia: 113.57 GB** | Ruang disk aman untuk manifest & artefak |

---

## 2. Status Runtime Python & Pustaka

* **Python Executable:** `C:\Users\nirvanaguys\AppData\Local\Programs\Python\Python313\python.exe`
* **Versi Python:** `3.13.9` (tags/v3.13.9:8183fa5)
* **Status Git:**
  * Root folder proyek `IPPL/` dan `daunku_ai/` saat ini **belum diinisialisasi Git**.
  * Git aktif terisolasi di dalam `daunku_app/` (aplikasi Flutter).

### Pustaka Terpasang untuk Data Science & Utilitas:
| Pustaka | Versi | Status Kompatibilitas Python 3.13 |
| :--- | :---: | :--- |
| `numpy` | 2.3.5 | Siap untuk manipulasi array & metrik |
| `pandas` | 3.0.2 | Siap untuk pemrosesan tabel & CSV |
| `Pillow (PIL)` | 12.2.0 | Siap untuk verifikasi gambar & visual sampling |
| `PyYAML` | 6.0.3 | Siap untuk konfigurasi |
| `scikit-learn` | 1.8.0 | Siap untuk stratified split & evaluasi |
| `matplotlib` | 3.10.8 | Siap untuk plot visual & confusion matrix |
| `fastapi` | 0.140.8 | Siap untuk inferensi API lokal (Tahap 12) |
| `uvicorn` | 0.49.0 | Server ASGI untuk FastAPI |

### Status Framework Deep Learning (Training):
| Framework | Status | Catatan Kompatibilitas |
| :--- | :---: | :--- |
| `torch` / `torchvision` | NOT INSTALLED | Wheel PyTorch untuk Windows Python 3.13 masih terbatas |
| `tensorflow` | NOT INSTALLED | TensorFlow resmi belum menyediakan wheel stabil untuk Python 3.13 Windows |
| `ultralytics (YOLO)` | NOT INSTALLED | Membutuhkan PyTorch |
| `onnxruntime` | NOT INSTALLED | Opsi ringan untuk inferensi di Python 3.13 |

---

## 3. Rekomendasi Teknis Lingkungan

1. **Pengembangan Lokal (Audit, Preprocessing, API):**
   * Lingkungan lokal saat ini (`Python 3.13.9`) sudah **sangat memadai** untuk seluruh tugas audit, validasi integritas dataset, pembuatan manifest kanonis, split data, penyusunan knowledge base, dan pembuatan API FastAPI.
2. **Strategi Training Model:**
   * Karena laptop tidak memiliki GPU NVIDIA dan PyTorch/TensorFlow pada Windows Python 3.13 masih memiliki kendala ketersediaan wheel pre-built, proses training model (Tahap 8) sebaiknya dijalankan di **Google Colab** (GPU T4/V100) menggunakan Python 3.10/3.11 yang sudah terpasang ekosistem ML lengkap.
   * Model hasil training (misal format `.onnx` atau `.tflite`) kemudian dibawa kembali ke lingkungan lokal untuk inferensi di layanan FastAPI DaunKu.
