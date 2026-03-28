#!/usr/bin/env python3
"""
Generate realistic Apache/Nginx-style web server access logs for testing.
Produces logs in Combined Log Format.
"""

import random
import datetime
import gzip
import os

# --- Config ---
NUM_ENTRIES = 20
OUTPUT_FILE = "access.log"

URLS = [
    "/", "/index.html", "/about", "/contact", "/products", "/products/shoes",
    "/products/hats", "/products/bags", "/cart", "/checkout", "/login",
    "/register", "/dashboard", "/api/v1/users", "/api/v1/products",
    "/api/v1/orders", "/static/main.css", "/static/app.js", "/favicon.ico",
    "/robots.txt", "/sitemap.xml", "/blog", "/blog/post-1", "/blog/post-2",
    "/blog/post-3", "/search?q=shoes", "/search?q=hats", "/404",
    "/admin", "/wp-login.php", "/xmlrpc.php",
]

STATUS_CODES = [
    (200, 65), (304, 10), (301, 5), (302, 3),
    (404, 8), (500, 3), (403, 3), (400, 2), (503, 1),
]

METHODS = [("GET", 80), ("POST", 15), ("PUT", 3), ("DELETE", 2)]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Android 13; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Bingbot/2.0 (+http://www.bing.com/bingbot.htm)",
    "curl/7.88.1",
    "python-requests/2.31.0",
]

REFERRERS = [
    "-", "https://google.com", "https://bing.com", "https://twitter.com",
    "https://facebook.com", "https://reddit.com", "https://example.com/",
    "https://example.com/blog",
]

IP_POOLS = {
    "heavy": ["192.168.1.1", "10.0.0.5", "203.45.67.89", "78.12.34.56"],
    "medium": [f"45.{r}.{c}.{d}" for r in range(1, 5) for c in range(1, 4) for d in range(1, 4)],
    "light": [f"{a}.{b}.{c}.{d}" for a in [66, 72, 88, 104, 120]
              for b in range(1, 6) for c in range(1, 4) for d in range(1, 6)],
}


def weighted_choice(choices):
    items, weights = zip(*choices)
    return random.choices(items, weights=weights, k=1)[0]


def random_ip():
    roll = random.random()
    if roll < 0.05:
        return random.choice(IP_POOLS["heavy"])
    elif roll < 0.30:
        return random.choice(IP_POOLS["medium"])
    else:
        return random.choice(IP_POOLS["light"])


def random_datetime():
    start = datetime.datetime(2024, 1, 1)
    end = datetime.datetime(2024, 6, 30)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    dt = start + datetime.timedelta(seconds=random_seconds)
    # Simulate traffic spikes during business hours
    if random.random() < 0.6:
        dt = dt.replace(hour=random.randint(8, 20))
    return dt


def generate_log_line():
    ip = random_ip()
    dt = random_datetime()
    method = weighted_choice(METHODS)
    url = random.choice(URLS)
    status = weighted_choice(STATUS_CODES)
    size = random.randint(200, 50000) if status == 200 else random.randint(100, 500)
    referrer = random.choice(REFERRERS)
    ua = random.choice(USER_AGENTS)
    response_time = random.randint(5, 3000)

    timestamp = dt.strftime("%d/%b/%Y:%H:%M:%S +0000")
    return (
        f'{ip} - - [{timestamp}] "{method} {url} HTTP/1.1" '
        f'{status} {size} "{referrer}" "{ua}" {response_time}'
    )


if __name__ == "__main__":
    print(f"Generating {NUM_ENTRIES} log entries → {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w") as f:
        for _ in range(NUM_ENTRIES):
            f.write(generate_log_line() + "\n")
    print(f"Done! File size: {os.path.getsize(OUTPUT_FILE) / 1024 / 1024:.2f} MB")
