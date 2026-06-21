# Laporan Metodologi Pengumpulan Data Lowongan Kerja Secara Otomatis

## 1. Pendahuluan

### 1.1 Latar Belakang
Pengumpulan data lowongan kerja secara manual dari berbagai portal memerlukan waktu dan tenaga yang besar. Untuk mendukung penelitian analisis kebutuhan skill tenaga kerja di bidang teknologi informasi, diperlukan sebuah sistem yang mampu mengumpulkan data lowongan kerja secara otomatis, terstruktur, dan konsisten.

### 1.2 Tujuan
Sistem ini dibangun untuk:
- Mengumpulkan data lowongan kerja dari portal **LinkedIn** dan **JobStreet** secara otomatis
- Membersihkan dan menormalisasi data sebelum disimpan
- Mengekstrak skill/teknologi yang dibutuhkan dari deskripsi lowongan
- Menyimpan data ke database cloud (Supabase/PostgreSQL)
- Menjadwalkan pengambilan data secara berkala (24 jam sekali)

---

## 2. Arsitektur Sistem

### 2.1 Diagram Alur

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   LinkedIn   │───▶│  Scraper    │───▶│  Cleaner &  │───▶│  Supabase   │
│  & JobStreet │    │ (Playwright)│    │  Normalizer │    │ (PostgreSQL)│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │
                   ┌──────┴──────┐
                   │  Scheduler  │
                   │ (24 jam)    │
                   └─────────────┘
```

### 2.2 Komponen Sistem

| Komponen | Modul | Fungsi |
|----------|-------|--------|
| **Scraper** | `linkedin.py`, `jobstreet.py` | Mengambil data mentah dari portal lowongan |
| **Browser Engine** | `browser.py` | Konfigurasi Playwright (Chromium headless) |
| **Simulasi Manusia** | `base.py` | Delay acak dan scroll untuk menghindari deteksi bot |
| **Pembersih Data** | `cleaner.py` | Validasi dan pembersihan data tidak valid |
| **Normalisasi** | `normalize.py` | Menyamakan format data dari berbagai sumber |
| **Ekstraksi Skill** | `skills_keyword.py` | Mencari skill/teknologi dari deskripsi lowongan |
| **Database** | `supabase_client.py` | Koneksi ke Supabase (PostgreSQL) |
| **Penjadwal** | `run.py` | Mengatur waktu eksekusi scraping otomatis |

---

## 3. Teknologi yang Digunakan

### 3.1 Python 3.10+
Bahasa pemrograman utama yang digunakan karena ekosistem data science yang kaya dan dukungan library web scraping yang lengkap.

### 3.2 Playwright (Headless Browser)
Playwright digunakan sebagai browser automation untuk mengambil data dari halaman web yang membutuhkan JavaScript rendering. Chromium dijalankan dalam mode **headless** (tanpa tampilan GUI) dengan konfigurasi:
- User-Agent realistis untuk menghindari deteksi
- Viewport 1280x800 pixel
- Disable fitur deteksi automasi (`--disable-blink-features=AutomationControlled`)

### 3.3 BeautifulSoup4
Library parsing HTML untuk mengekstrak data dari konten halaman web yang sudah di-render oleh Playwright.

### 3.4 Supabase (PostgreSQL)
Database cloud berbasis PostgreSQL yang menyimpan data lowongan kerja. Digunakan karena:
- Gratis untuk proyek skala kecil
- mendukung JSONB untuk menyimpan array skill
- REST API bawaan untuk akses data

### 3.5 Schedule
Library penjadwalan sederhana untuk menjalankan scraping secara berkala setiap 24 jam.

---

## 4. Proses Pengumpulan Data

### 4.1 Alur Scraping
1. **Inisialisasi Browser** — Playwright membuka Chromium headless
2. **Navigasi** — Menuju halaman pencarian lowongan dengan kata kunci tertentu
3. **Simulasi Manusia** — Delay acak 2-6 detik dan scroll halaman
4. **Parsing** — BeautifulSoup mengekstrak data dari HTML
5. **Detail Halaman** — Membuka halaman detail setiap lowongan untuk deskripsi lengkap
6. **Ekstraksi Skill** — Pattern matching terhadap database 100+ skill teknologi
7. **Pembersihan** — Validasi data (judul, perusahaan, URL harus valid)
8. **Normalisasi** — Menyamakan format dari LinkedIn dan JobStreet
9. **Penyimpanan** — Upsert ke Supabase (berdasarkan URL sebagai unique key)
10. **Penutupan Browser** — Melepaskan resource

### 4.2 Strategi Anti-Deteksi
| Strategi | Implementasi |
|----------|-------------|
| **User-Agent Realistis** | Menggunakan string User-Agent Chrome 120 terbaru |
| **Headless Mode** | Chromium berjalan tanpa GUI |
| **Human Delay** | Jeda acak 2-6 detik antar aksi |
| **Scroll Simulasi** | Scroll setengah halaman untuk mensimulasikan perilaku manusia |
| **Timeout Handling** | Fallback dari `networkidle` ke `domcontentloaded` jika timeout |

### 4.3 Data yang Dikumpulkan

| Field | Keterangan | Contoh |
|-------|-----------|--------|
| `title` | Judul posisi | "Software Engineer" |
| `company` | Nama perusahaan | "PT Maju Bersama" |
| `location` | Lokasi kerja | "Jakarta, Indonesia" |
| `type` | Tipe pekerjaan | "Full-time" |
| `description` | Deskripsi lengkap lowongan | (teks panjang) |
| `skills` | Array skill yang terdeteksi | `["python", "react", "postgresql"]` |
| `url` | URL unik lowongan | "https://linkedin.com/jobs/view/..." |
| `source` | Sumber data | "LinkedIn" / "JobStreet" |

---

## 5. Database Schema

```sql
CREATE TABLE public.jobs (
    id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title         TEXT NOT NULL,
    company       TEXT NOT NULL,
    location      TEXT NOT NULL,
    type          TEXT NOT NULL DEFAULT 'Full-time'
                    CHECK (type IN ('Full-time','Part-time','Contract','Internship')),
    salary        TEXT,
    description   TEXT NOT NULL,
    skills        JSONB DEFAULT '[]'::jsonb,
    contact_info  TEXT,
    url           TEXT NOT NULL UNIQUE,
    source        TEXT NOT NULL,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Indeks:**
- `idx_jobs_source` — Mempercepat query berdasarkan sumber data
- `idx_jobs_is_active` — Mempercepat filter lowongan aktif

**Trigger:**
- `trg_jobs_updated_at` — Otomatis memperbarui `updated_at` saat data diubah

---

## 6. Ekstraksi Skill

Sistem menggunakan pendekatan **keyword matching** dengan database 100+ skill teknologi yang dikategorikan:

| Kategori | Contoh Skill |
|----------|-------------|
| **Bahasa Pemrograman** | Python, JavaScript, TypeScript, Java, Go, Kotlin |
| **Frontend** | React, Vue, Angular, Next.js, Tailwind CSS |
| **Backend** | Node.js, Django, FastAPI, Spring Boot, Laravel |
| **Database** | PostgreSQL, MySQL, MongoDB, Redis |
| **Cloud & DevOps** | AWS, Azure, Docker, Kubernetes, Terraform |
| **Data & ML** | TensorFlow, PyTorch, Pandas, Scikit-learn |
| **Mobile** | Flutter, React Native, Swift, Kotlin |
| **Testing** | Selenium, Jest, Pytest, Cypress |
| **Metodologi** | Agile, Scrum, CI/CD, REST API, GraphQL |

---

## 7. Penjadwalan Otomatis

Sistem berjalan dalam loop continuous dengan mekanisme:

```python
schedule.every(24).hours.do(main)  # Scraping setiap 24 jam
while running:
    schedule.run_pending()
    time.sleep(60)  # Cek setiap 1 menit
```

**Graceful Shutdown:**
- `Ctrl+C` → menangkap signal `SIGINT` → menghentikan loop dengan rapi
- `SIGTERM` → mendukung penghentian dari process manager

---

## 8. Analisis Risiko dan Etika

### 8.1 Risiko Teknis
| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Perubahan struktur HTML | Scraper berhenti bekerja | Multiple selector fallback |
| Deteksi bot / IP ban | Data tidak bisa diambil | Human delay, user-agent realistis |
| Halaman timeout | Data tidak lengkap | Timeout handling + fallback |
| Data duplikat | Database tidak bersih | Upsert berdasarkan URL unik |

### 8.2 Pertimbangan Hukum & Etika
- **Terms of Service:** LinkedIn dan JobStreet secara teknis melarang scraping otomatis. Namun, pengambilan dilakukan dengan volume rendah dan tidak mengambil data pribadi pelamar.
- **UU Pelindungan Data Pribadi (PDP):** Sistem hanya mengambil data publik lowongan kerja (judul, perusahaan, deskripsi), bukan data pribadi pelamar.
- **Etika:** Delay antar request diimplementasikan untuk tidak memberatkan server target.
- **Disclaimer:** Untuk keperluan akademik, pengambilan data ini dilakukan secara terbatas dan tidak untuk komersialisasi.

### 8.3 Sumber Data Alternatif (Riset)

| Portal | Izin Scraping | API Publik | Status |
|--------|---------------|------------|--------|
| LinkedIn | ❌ Tidak | Terbatas (berbayar) | ✅ Digunakan |
| JobStreet | ❌ Tidak | Tidak ada | ✅ Digunakan |
| Glints | ❌ Tidak (ToS eksplisit) | Tidak ada | ❌ Tidak digunakan |
| Indeed | ❌ Tidak (robots.txt) | Hanya untuk partner ATS | ❌ Tidak digunakan |
| Kalibrr | ❌ Tidak (ToS eksplisit) | Tidak ada | ❌ Tidak digunakan |
| Karir.com | ❌ Tidak | Tidak ada | ❌ Tidak digunakan |

> **Catatan:** Hanya LinkedIn dan JobStreet yang digunakan karena pertimbangan stabilitas scraper dan risiko hukum.

---

## 9. Hasil dan Pengujian

### 9.1 Struktur Output
Data tersimpan di Supabase dengan format JSON:
```json
{
  "title": "Software Engineer",
  "company": "PT Teknologi Nusantara",
  "location": "Jakarta, Indonesia",
  "type": "Full-time",
  "description": "Kami mencari software engineer...",
  "skills": ["python", "react", "postgresql", "docker"],
  "url": "https://linkedin.com/jobs/view/123456",
  "source": "LinkedIn",
  "is_active": true
}
```

### 9.2 File Struktur Proyek

```
anggi-skripsi/
├── run.py                 # Entry point & scheduler
├── linkedin.py            # Scraper LinkedIn
├── jobstreet.py           # Scraper JobStreet
├── browser.py             # Konfigurasi Playwright
├── base.py                # Helper delay & scroll
├── cleaner.py             # Pembersihan data
├── normalize.py           # Normalisasi format
├── skills_keyword.py      # Database skill & ekstraksi
├── supabase_client.py     # Koneksi Supabase
├── schema.sql             # Database schema
├── requirements.txt       # Dependensi Python
├── test_all.py            # Unit test
└── .env                   # Environment variables (tidak di-commit)
```

---

## 10. Kesimpulan

Sistem scraping otomatis ini berhasil mengumpulkan data lowongan kerja dari LinkedIn dan JobStreet dengan fitur:
- ✅ Scraping otomatis dengan headless browser
- ✅ Pembersihan dan normalisasi data
- ✅ Ekstraksi 100+ skill teknologi dari deskripsi
- ✅ Penyimpanan ke database cloud (Supabase)
- ✅ Penjadwalan 24 jam sekali
- ✅ Graceful shutdown (Ctrl+C)

Sistem ini dapat digunakan sebagai dasar untuk analisis tren kebutuhan skill di pasar kerja teknologi Indonesia.

---

*Dokumen ini disusun untuk keperluan skripsi.*
*Terakhir diperbarui: Juni 2026*
