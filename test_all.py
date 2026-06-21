"""
Test suite untuk memverifikasi semua komponen sebelum scraping penuh.
Jalankan: python test_all.py
"""

import sys
import traceback


def section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print('='*50)


def ok(msg):
    print(f"  [OK] {msg}")


def fail(msg):
    print(f"  [FAIL] {msg}")


# ─────────────────────────────────────────────
# TEST 1: cleaner
# ─────────────────────────────────────────────
section("TEST 1: cleaner.py")

try:
    from cleaner import clean_job

    # valid
    result = clean_job({"company": "  Google  ", "title": "  Software Engineer  ", "url": "  https://example.com  ", "location": "  Jakarta  ", "description": "  Need Python  ", "skills": ["python", "react"]})
    assert result is not None, "Harus lolos validasi"
    assert result["company"] == "Google", f"company harus di-strip, dapat: {result['company']}"
    assert result["title"] == "Software Engineer", f"title harus di-strip, dapat: {result['title']}"
    assert result["url"] == "https://example.com", f"url harus di-strip, dapat: {result['url']}"
    assert result["location"] == "Jakarta", f"location harus di-strip, dapat: {result['location']}"
    assert result["description"] == "Need Python", f"description harus di-strip, dapat: {result['description']}"
    assert result["skills"] == ["python", "react"], f"skills harus dipertahankan, dapat: {result['skills']}"
    ok("clean_job mengembalikan dict yang sudah di-strip dengan semua field")

    # valid tanpa location/description/skills — harus ada default
    result2 = clean_job({"company": "Google", "title": "Software Engineer", "url": "https://example.com"})
    assert result2["location"] == "Indonesia", f"location default Indonesia, dapat: {result2['location']}"
    assert result2["description"] == "", f"description default kosong, dapat: {result2['description']}"
    assert result2["skills"] == [], f"skills default [], dapat: {result2['skills']}"
    ok("clean_job memberikan default untuk location, description, skills")

    # company terlalu pendek
    assert clean_job({"company": "A", "title": "Software Engineer", "url": "https://x.com"}) is None
    ok("Menolak company < 2 karakter")

    # title terlalu pendek
    assert clean_job({"company": "Google", "title": "Dev", "url": "https://x.com"}) is None
    ok("Menolak title < 5 karakter")

    # URL tidak valid
    assert clean_job({"company": "Google", "title": "Software Engineer", "url": "/relative/path"}) is None
    ok("Menolak URL yang tidak diawali http")

    # field kosong
    assert clean_job({"company": "", "title": "Software Engineer", "url": "https://x.com"}) is None
    ok("Menolak company kosong")

    assert clean_job({"company": "Google", "title": "", "url": "https://x.com"}) is None
    ok("Menolak title kosong")

    assert clean_job({"company": "Google", "title": "Software Engineer", "url": ""}) is None
    ok("Menolak url kosong")

except Exception as e:
    fail(f"cleaner.py error: {e}")
    traceback.print_exc()


# ─────────────────────────────────────────────
# TEST 2: skills_keyword
# ─────────────────────────────────────────────
section("TEST 2: skills_keyword.py")

try:
    from skills_keyword import extract_skills

    desc = "We need a developer proficient in Python, JavaScript, React, and PostgreSQL. Experience with Docker and AWS is a plus."
    skills = extract_skills(desc)
    assert "python" in skills, f"Harus detect python, dapat: {skills}"
    assert "javascript" in skills, f"Harus detect javascript, dapat: {skills}"
    assert "react" in skills, f"Harus detect react, dapat: {skills}"
    assert "postgresql" in skills, f"Harus detect postgresql, dapat: {skills}"
    assert "docker" in skills, f"Harus detect docker, dapat: {skills}"
    assert "aws" in skills, f"Harus detect aws, dapat: {skills}"
    ok(f"extract_skills menemukan {len(skills)} skill: {skills}")

    # Empty text
    assert extract_skills("") == []
    ok("extract_skills mengembalikan [] untuk teks kosong")

    # No matching skills
    assert extract_skills("we need a fast learner") == []
    ok("extract_skills mengembalikan [] untuk teks tanpa skill")

except Exception as e:
    fail(f"skills_keyword.py error: {e}")
    traceback.print_exc()


# ─────────────────────────────────────────────
# TEST 3: normalize
# ─────────────────────────────────────────────
section("TEST 3: normalize.py")

try:
    from normalize import normalize

    job = {"company": "Google", "title": "Software Engineer", "url": "https://example.com", "location": "Jakarta", "description": "Need Python and React skills", "skills": ["python", "react"]}
    row = normalize(job, "LinkedIn")

    assert row["company"] == "Google", f"Dapat: {row['company']}"
    assert row["title"] == "Software Engineer", f"Dapat: {row['title']}"
    assert row["url"] == "https://example.com", f"Dapat: {row['url']}"
    assert row["source"] == "LinkedIn", f"Dapat: {row['source']}"
    assert row["is_active"] is True, f"Dapat: {row['is_active']}"
    assert row["location"] == "Jakarta", f"Dapat: {row['location']}"
    assert row["description"] == "Need Python and React skills", f"Dapat: {row['description']}"
    assert row["skills"] == ["python", "react"], f"Dapat: {row['skills']}"
    ok("normalize menghasilkan dict dengan semua kolom yang benar")

    # Fallback description when not provided
    job2 = {"company": "Google", "title": "Software Engineer", "url": "https://example.com"}
    row2 = normalize(job2, "JobStreet")
    assert row2["description"] == "Software Engineer", "Fallback ke title jika description kosong"
    ok("normalize fallback ke title saat description tidak ada")

except Exception as e:
    fail(f"normalize.py error: {e}")
    traceback.print_exc()


# ─────────────────────────────────────────────
# TEST 4: supabase_client
# ─────────────────────────────────────────────
section("TEST 4: supabase_client.py (koneksi)")

try:
    from supabase_client import supabase

    # Coba query sederhana — hanya mengecek koneksi, bukan data
    result = supabase.table("jobs").select("id").limit(1).execute()
    ok(f"Koneksi Supabase berhasil. Baris tersedia: {len(result.data)}")

except Exception as e:
    fail(f"Koneksi Supabase gagal: {e}")
    traceback.print_exc()


# ─────────────────────────────────────────────
# TEST 5: push (pipeline lengkap tanpa scraping)
# ─────────────────────────────────────────────
section("TEST 5: push() pipeline (mock data)")

try:
    from run import push

    mock_jobs = [
        {"company": "Test Company", "title": "Backend Developer", "url": "https://test.example.com/job/1"},
        {"company": "  Spasi Inc  ", "title": "  Frontend Dev Test  ", "url": "  https://test.example.com/job/2  "},
        # data invalid — harus dibuang
        {"company": "X", "title": "Dev", "url": "/relative"},
        {"company": "", "title": "Backend Developer", "url": "https://test.example.com/job/3"},
        # duplikat URL
        {"company": "Test Company", "title": "Backend Developer", "url": "https://test.example.com/job/1"},
    ]

    inserted = push(mock_jobs, "TestSource")
    assert inserted == 2, f"Harus 2 yang valid & unik, dapat: {inserted}"
    ok(f"push() memasukkan {inserted} baris (duplikat & invalid dibuang dengan benar)")

except Exception as e:
    fail(f"push() error: {e}")
    traceback.print_exc()


# ─────────────────────────────────────────────
# TEST 6: browser
# ─────────────────────────────────────────────
section("TEST 6: browser.py (Playwright launch)")

try:
    from browser import get_browser

    p, browser, context = get_browser()
    page = context.new_page()
    page.goto("about:blank")
    assert page.title() == ""
    browser.close()
    p.stop()
    ok("Browser Playwright berhasil diluncurkan dan ditutup")

except Exception as e:
    fail(f"browser.py error: {e}")
    traceback.print_exc()


# ─────────────────────────────────────────────
# RINGKASAN
# ─────────────────────────────────────────────
section("SELESAI")
print("  Semua test selesai dijalankan.")
print("  Cek hasil [OK]/[FAIL] di atas.\n")
