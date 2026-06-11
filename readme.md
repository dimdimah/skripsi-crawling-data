# Job Scraper

Proyek ini adalah scraper lowongan kerja yang mengumpulkan data dari LinkedIn dan JobStreet, membersihkannya, lalu menyimpannya ke database Supabase.

## Fitur

- Scraping lowongan dari **LinkedIn** dan **JobStreet**
- Automasi browser menggunakan Playwright
- Pembersihan dan normalisasi data sebelum disimpan
- Penyimpanan data ke Supabase dengan mekanisme upsert
- Penjadwalan scraping setiap 24 jam

## Setup

1. Clone repository ini
2. Buat virtual environment (disarankan Python 3.10+):

    python -m venv venv
    venv\Scripts\activate

3. Install dependensi:

    pip install -r requirements.txt

4. Instal browser untuk Playwright:

    playwright install chromium

5. Buat file `.env` di direktori proyek:

    SUPABASE_URL=your_supabase_url
    SUPABASE_ANON_KEY=your_supabase_anon_key

6. Jalankan scraper:

    python run.py

## Struktur Modul

- `run.py` - Entry point, menjadwalkan scraping dan menyimpan data
- `linkedin.py` - Scraping lowongan dari LinkedIn
- `jobstreet.py` - Scraping lowongan dari JobStreet
- `browser.py` - Konfigurasi Playwright (Chromium headless)
- `base.py` - Helper delay dan scroll untuk simulasi manusia
- `normalize.py` - Normalisasi format data sebelum disimpan
- `cleaner.py` - Validasi dan pembersihan data yang tidak valid
- `supabase_client.py` - Koneksi ke Supabase

## Database

Pastikan tabel `lowongan_kerja` sudah ada di Supabase dengan kolom:
- `nama_perusahaan`
- `posisi_jabatan`
- `deskripsi_kualifikasi`
- `link_pendaftaran`
- `sumber_data`
- `is_active`

Kolom `link_pendaftaran` digunakan sebagai konflik untuk upsert.
