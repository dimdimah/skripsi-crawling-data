from bs4 import BeautifulSoup
from browser import get_browser
from base import human_delay, jitter_scroll
from urllib.parse import urljoin
from skills_keyword import extract_skills


def scrape_linkedin(keyword="software engineer"):
    p, browser, context = get_browser()
    page = context.new_page()

    base_url = "https://www.linkedin.com"
    url = f"{base_url}/jobs/search/?keywords={keyword}&location=Indonesia"

    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
    except Exception:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

    human_delay()
    jitter_scroll(page)
    human_delay()

    soup = BeautifulSoup(page.content(), "html.parser")

    jobs = []

    # LinkedIn public job cards use these class patterns
    cards = soup.select("div.base-card")

    for card in cards:
        try:
            title_el = card.select_one(
                "h3.base-search-card__title, "
                "span.screen-reader-text, "
                "h3"
            )
            company_el = card.select_one(
                "h4.base-search-card__subtitle, "
                "a.hidden-nested-link, "
                "h4"
            )
            location_el = card.select_one(
                "span.job-search-card__location, "
                "span[class*='location']"
            )
            link_el = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")

            if not (title_el and company_el and link_el):
                continue

            href = link_el.get("href", "")
            if href.startswith("http"):
                job_url = href.split("?")[0]
            else:
                job_url = urljoin(base_url, href.split("?")[0])

            location_text = location_el.text.strip() if location_el else ""

            # Visit detail page for description
            description = ""
            skills = []
            try:
                detail_page = context.new_page()
                detail_page.goto(job_url, wait_until="domcontentloaded", timeout=15000)
                human_delay()
                detail_soup = BeautifulSoup(detail_page.content(), "html.parser")

                # LinkedIn description sections
                desc_el = detail_soup.select_one(
                    "div.description__text, "
                    "div[class*='description'], "
                    "section[class*='description']"
                )
                if desc_el:
                    description = desc_el.text.strip()

                # Extract location from detail if not found in listing
                if not location_text:
                    loc_el = detail_soup.select_one(
                        "div[class*='location'], "
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
                "title": title_el.text.strip(),
                "company": company_el.text.strip(),
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