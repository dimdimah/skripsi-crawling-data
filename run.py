from linkedin import scrape_linkedin
from jobstreet import scrape_jobstreet
from normalize import normalize
from cleaner import clean_job
from supabase_client import supabase
import time
import schedule
import signal
import sys


def push(jobs, source):
    batch = []
    seen = set()

    for job in jobs:
        job = clean_job(job)
        if not job:
            continue

        url = job["url"]
        if url in seen:
            continue
        seen.add(url)

        batch.append(normalize(job, source))

    if not batch:
        return 0

    try:
        supabase.table("jobs") \
            .upsert(batch, on_conflict="url") \
            .execute()
    except Exception as e:
        print(f"[ERROR] Supabase upsert gagal ({source}): {e}")
        return 0

    return len(batch)


def main():
    try:
        print("Scraping LinkedIn...")
        linkedin_jobs = scrape_linkedin()
        print(f"LinkedIn ditemukan: {len(linkedin_jobs)}, dimasukkan: {push(linkedin_jobs, 'LinkedIn')}")

        print("Scraping JobStreet...")
        jobstreet_jobs = scrape_jobstreet()
        print(f"JobStreet ditemukan: {len(jobstreet_jobs)}, dimasukkan: {push(jobstreet_jobs, 'JobStreet')}")
    except Exception as e:
        print(f"[ERROR] Scraping gagal: {e}")


running = True


def shutdown(signum, frame):
    global running
    print("\n[INFO] Ctrl+C ditekan. Menghentikan scraper...")
    running = False


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    main()  # jalankan langsung saat pertama kali start

    schedule.every(24).hours.do(main)
    print("Job scraper berjalan setiap 24 jam...")
    print("Tekan Ctrl+C untuk menghentikan.")

    while running:
        schedule.run_pending()
        time.sleep(60)

    print("[INFO] Scraper dihentikan. Sampai jumpa!")
    sys.exit(0)
