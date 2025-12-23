# Sistem Manajemen Aset Berbasis Barcode

Aplikasi web ini digunakan untuk **mengelola data aset** menggunakan **barcode / QR Code**, mulai dari menambah aset, melihat daftar aset, memperbarui kondisi, menghapus aset, hingga melakukan scan barcode melalui kamera maupun gambar.

Dibangun menggunakan **Python + Streamlit**, aplikasi ini cocok digunakan untuk mengatur inventaris rumah tangga.

# Anggota Kelompok
1. Muhammad Fathurrohim 24020007
2. Bahtiar Rehan Asafa 24020089
3. Muhammad Nadif Waluyo 24020021
4. Maulana Yusuf 24020029

##  Fitur Utama

-  Login admin sederhana
-  Tambah aset + generate QR Code
-  Lihat daftar aset (dengan pencarian)
-  Update kondisi aset (baik / rusak / hilang)
-  Hapus aset
-  Scan barcode via kamera
-  Scan barcode dari gambar
-  Log aktivitas (tambah, update, hapus)
-  Tampilan modern & estetik


## Teknologi yang Digunakan

- Python 3.x  
- Streamlit  
- Pandas  
- Pillow (PIL)  
- streamlit-option-menu  
- streamlit-webrtc  
- OpenCV(scannerbarcode)  
- NumPy
- PyZBar
- python-barcode (Code128)
- PyAV (av)
- OS (os)
- Datetime

## Struktur Folder

project/
│
├── app.py                 # File utama aplikasi
├── utils.py               # Fungsi helper (load, save, log, QR)
├── barcode_scanner.py     # Scanner barcode via kamera
│
├── data/
│   ├── master.csv         # Data aset
│   └── log.csv            # Log aktivitas
│
├── qr/
│   └── *.png              # QR Code aset
│
├── requirements.txt
└── README.md

