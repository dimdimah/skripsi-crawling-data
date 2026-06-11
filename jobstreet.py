from bs4 import BeautifulSoup
from browser import get_browser
from base import human_delay, jitter_scroll


def scrape_jobstreet(keyword="developer"):
    p, browser, context = get_browser()
    page = context.new_page()

    url = f"https://www.jobstreet.co.id/id/job-search/{keyword}-jobs/"

    page.goto(url, wait_until="domcontentloaded")
    human_delay()

    jitter_scroll(page)
    human_delay()

    soup = BeautifulSoup(page.content(), "html.parser")

    jobs = []

    cards = soup.select("article")

    for card in cards:
        try:
            title = card.select_one("a")
            company = card.select_one("span")

            if title:
                jobs.append({
                    "title": title.text.strip(),
                    "company": company.text.strip() if company else "",
                    "url": title["href"]
                })
        except:
            continue

    browser.close()
    p.stop()

    return jobs