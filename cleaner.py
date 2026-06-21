def clean_job(job):
    company = job.get("company")
    title = job.get("title")
    url = job.get("url")

    if not company or not title or not url:
        return None

    company = company.strip()
    title = title.strip()
    url = url.strip()

    if len(company) < 2 or len(title) < 5:
        return None

    if not url.startswith("http"):
        return None

    return {
        "company": company,
        "title": title,
        "url": url,
        "location": (job.get("location") or "").strip() or "Indonesia",
        "description": (job.get("description") or "").strip(),
        "skills": job.get("skills", []),
    }