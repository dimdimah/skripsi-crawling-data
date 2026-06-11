import random
import time

def human_delay(min_sec=2, max_sec=6):
    time.sleep(random.uniform(min_sec, max_sec))


def jitter_scroll(page):
    page.evaluate("""
        window.scrollTo(0, document.body.scrollHeight / 2);
    """)