from linkedin import scrape_linkedin
from jobstreet import scrape_jobstreet
from normalize import normalize
from cleaner import clean_job
from supabase_client import supabase
import time
import schedule


def push(jobs, source):
    batch = []
    seen = set()

    for job in jobs:

        # CLEANING STEP
        job = clean_job(job)
        if not job:
            continue

        url = job["url"]

        if url in seen:
            continue
        seen.add(url)

        batch.append(normalize(job, source))

    if batch:
        supabase.table("lowongan_kerja") \
            .upsert(batch, on_conflict="link_pendaftaran") \
            .execute()

    return len(batch)


def main():
    try:
        print("Scraping LinkedIn...")
        linkedin_jobs = scrape_linkedin()
        print("LinkedIn inserted:", push(linkedin_jobs, "LinkedIn"))

        print("Scraping JobStreet...")
        jobstreet_jobs = scrape_jobstreet()
        print("JobStreet inserted:", push(jobstreet_jobs, "JobStreet"))
    except Exception as e:
        print(f"Error during scraping: {e}")


if __name__ == "__main__":
    schedule.every(24).hours.do(main)
    
    print("Job scraper running every 24 hours...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute