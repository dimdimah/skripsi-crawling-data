from bs4 import BeautifulSoup
from browser import get_browser
from base import human_delay, jitter_scroll


def scrape_linkedin(keyword="software engineer"):
    p, browser, context = get_browser()
    page = context.new_page()

    url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}"

    page.goto(url, wait_until="domcontentloaded")
    human_delay()

    jitter_scroll(page)
    human_delay()

    soup = BeautifulSoup(page.content(), "html.parser")

    jobs = []

    cards = soup.select("li")

    for card in cards:
        try:
            title = card.select_one("h3")
            company = card.select_one("h4")
            link = card.select_one("a")

            if title and company and link:
                jobs.append({
                    "title": title.text.strip(),
                    "company": company.text.strip(),
                    "url": "https://www.linkedin.com" + link["href"]
                })
        except:
            continue

    browser.close()
    p.stop()

    return jobs