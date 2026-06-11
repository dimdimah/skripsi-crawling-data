def clean_job(job):
    company = job.get("company")
    title = job.get("title")
    url = job.get("url")

    # safety check
    if not company or not title or not url:
        return None

    company = company.strip()
    title = title.strip()
    url = url.strip()

    if len(company) < 2 or len(title) < 5:
        return None

    if not url.startswith("http"):
        return None

    return job