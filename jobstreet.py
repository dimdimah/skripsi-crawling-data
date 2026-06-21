from bs4 import BeautifulSoup
from browser import get_browser
from base import human_delay, jitter_scroll
from urllib.parse import urljoin
from skills_keyword import extract_skills


def scrape_jobstreet(keyword="developer"):
    p, browser, context = get_browser()
    page = context.new_page()

    base_url = "https://id.jobstreet.com"
    url = f"{base_url}/id/{keyword}-jobs"

    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
    except Exception:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

    human_delay()
    jitter_scroll(page)
    human_delay()

    soup = BeautifulSoup(page.content(), "html.parser")

    jobs = []

    # JobStreet job cards are wrapped in <article> elements
    cards = soup.select("article[data-testid='job-card'], article[data-automation='job-card'], article")

    for card in cards:
        try:
            # Job title link
            title_el = card.select_one(
                "a[data-automation='jobTitle'], "
                "h1[data-automation='job-detail-title'], "
                "a[data-testid='job-title'], "
                "h3 a, h2 a, a[href*='/job/']"
            )
            # Company name
            company_el = card.select_one(
                "span[data-automation='jobCompany'], "
                "a[data-automation='jobCompany'], "
                "[data-testid='company-name'], "
                "span[class*='company'], "
                "a[class*='company']"
            )
            # Location
            location_el = card.select_one(
                "span[data-automation='jobLocation'], "
                "span[class*='location'], "
                "[data-testid='job-location']"
            )

            if not title_el:
                continue

            title_text = title_el.text.strip()
            company_text = company_el.text.strip() if company_el else ""
            location_text = location_el.text.strip() if location_el else ""

            href = title_el.get("href", "")
            if not href:
                continue

            if href.startswith("http"):
                job_url = href.split("?")[0]
            else:
                job_url = urljoin(base_url, href.split("?")[0])

            # Visit detail page for description
            description = ""
            skills = []
            try:
                detail_page = context.new_page()
                detail_page.goto(job_url, wait_until="domcontentloaded", timeout=15000)
                human_delay()
                detail_soup = BeautifulSoup(detail_page.content(), "html.parser")

                # JobStreet description sections
                desc_el = detail_soup.select_one(
                    "div[data-automation='jobAdDetails'], "
                    "div[class*='description'], "
                    "section[class*='description'], "
                    "article"
                )
                if desc_el:
                    description = desc_el.text.strip()

                # Extract location from detail if not found in listing
                if not location_text:
                    loc_el = detail_soup.select_one(
                        "span[data-automation='jobLocation'], "
                        "span[class*='location']"
                    )
                    if loc_el:
                        location_text = loc_el.text.strip()

                detail_page.close()
            except Exception:
                pass

            if not location_text:
                location_text = "Indonesia"

            skills = extract_skills(description)

            jobs.append({
                "title": title_text,
                "company": company_text,
                "location": location_text,
                "url": job_url,
                "description": description,
                "skills": skills,
            })
        except Exception:
            continue

    browser.close()
    p.stop()

    return jobs