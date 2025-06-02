# Peta Prakiraan Daerah Penangkapan Ikan Nasional (PPDPI Nasional) - Ilham Habibullah

Aplikasi ini adalah aplikasi web interaktif berbasis Python yang menggunakan pustaka `shiny` untuk menampilkan dan mengunduh peta serta tabel Prakiraan Daerah Penangkapan Ikan (DPI) dari server FTP berdasarkan area dan tanggal yang dipilih pengguna. Aplikasi ini dikembangkan untuk mendukung Kementerian Kelautan dan Perikanan Republik Indonesia dalam mendistribusikan data prakiraan kepada pengguna seperti nelayan dan peneliti.

## Tampilan Aplikasi
![Tampilan Aplikasi PPDPI Nasional](https://raw.githubusercontent.com/IlhamHabibullah/Landing-Pages-Shiny-App/main/tampilan-antar-muka.png)

## Tujuan Aplikasi
Aplikasi ini dirancang untuk:
1. **Menampilkan Peta dan Tabel DPI**: Menyediakan antarmuka pengguna untuk memilih area Wilayah Pengelolaan Perikanan Negara Republik Indonesia (WPP NRI) dan tanggal, kemudian mengunduh dan menampilkan file gambar peta (`peta_dpi_[area]_[tanggal].png`) dan tabel (`tabel_dpi_[area]_[tanggal].png`) dari server FTP.
2. **Interaksi Pengguna**: Memungkinkan pengguna untuk memilih area (misalnya, 571, 712, dll.) dan tanggal melalui kalender interaktif, melihat pratinjau gambar, memperbesar gambar, serta mengunduh file.
3. **Manajemen Unduhan**: Melacak jumlah unduhan untuk setiap file peta dan tabel berdasarkan area dan tanggal.

## Fungsi Utama
### Koneksi FTP
- Fungsi `download_from_ftp` mengambil file gambar (peta dan tabel) dari server FTP berdasarkan area dan tanggal yang dipilih.
- File disimpan sementara di direktori temporer lokal untuk ditampilkan dan diunduh.

### Antarmuka Pengguna
Menggunakan pustaka `shiny` untuk membuat antarmuka interaktif dengan elemen berikut:
- Dropdown untuk memilih area WPP NRI.
- Kalender interaktif untuk memilih tanggal, menampilkan dua bulan sekaligus dengan navigasi prev/next.
- Tombol unduh untuk mengunduh file peta dan tabel.
- Tombol perbesar untuk melihat gambar dalam modal pop-up.
- Footer dengan informasi kontak dan logo Kementerian Kelautan dan Perikanan.

### Fitur Interaktif
- Kalender kustom yang menampilkan tanggal dengan status "selected" dan "today".
- Spinner loading saat file diunduh dari FTP.
- Modal untuk memperbesar gambar peta dan tabel.
- Penghitung unduhan untuk melacak jumlah unduhan per file.

### Manajemen File
- File gambar diunduh dari server FTP dan dikonversi ke format base64 untuk ditampilkan di browser.
- Jika file tidak ditemukan, pesan error ditampilkan.

### Logging
- Menggunakan modul `logging` untuk mencatat aktivitas aplikasi (debug, error, dll.) untuk helping debugging.

## Struktur Kode
- **UI (`app_ui`)**: Mendefinisikan tata letak antarmuka menggunakan `ui.page_fluid`, termasuk header, form input, kalender, area konten untuk peta dan tabel, serta footer.
- **Server Logic (`server`)**: Menangani logika aplikasi, seperti:
  - Mengambil input pengguna (area dan tanggal).
  - Mengunduh file dari FTP.
  - Merender peta dan tabel sebagai gambar atau pesan error.
  - Mengelola navigasi kalender (prev/next month).
  - Menangani unduhan dan perbesaran gambar.
- **CSS dan JavaScript**: Menyediakan gaya visual dan interaktivitas, seperti animasi spinner, responsivitas, dan pengelolaan modal.

## Konteks Penggunaan
Aplikasi ini digunakan oleh Kementerian Kelautan dan Perikanan Republik Indonesia untuk mendistribusikan peta dan tabel DPI kepada pengguna, seperti nelayan atau peneliti, untuk membantu perencanaan penangkapan ikan berdasarkan data prakiraan.

## Prasyarat
- Python 3.10 atau lebih tinggi.
- Pustaka Python:
  - `shiny`
  - `ftplib`
  - `tempfile`
  - `base64`
  - `datetime`
  - `python-dateutil`
  - `shutil`
- Koneksi ke server FTP dengan kredensial yang valid.

## HAK CIPTA
Ilham Habibullah

## Hubungi
Ikuti saya di media sosial untuk pembaruan lebih lanjut:
- [Instagram](https://www.instagram.com/masllhamm_/) 📸
  
## Lisensi
© Copyright 2024 Kementerian Kelautan dan Perikanan Republik Indonesia. Hak cipta dilindungi.
