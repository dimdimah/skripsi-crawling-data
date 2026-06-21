def normalize(job, source):
    return {
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location", "Indonesia"),
        "type": job.get("type", "Full-time"),
        "description": job.get("description") or job.get("title", ""),
        "skills": job.get("skills", []),
        "url": job.get("url"),
        "source": source,
        "is_active": True
    }