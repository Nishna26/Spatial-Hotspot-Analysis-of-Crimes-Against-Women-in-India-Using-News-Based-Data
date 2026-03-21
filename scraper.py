# =========================================
# IMPORT LIBRARIES
# =========================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import json
import re

from config import HEADERS, NEWS_SOURCES, RAW_FILE


# =========================================
# LINK EXTRACTION
# =========================================

def get_article_links(page_url, source):

    try:

        r = requests.get(page_url, headers=HEADERS, timeout=15)

        soup = BeautifulSoup(r.text, "html.parser")

        links = set()

        for a in soup.find_all("a", href=True):

            href = a["href"]

            # convert relative links
            if href.startswith("/"):
                base = page_url.split("/")[0] + "//" + page_url.split("/")[2]
                href = base + href

            href = href.lower()

            # -------------------------
            # SOURCE SPECIFIC FILTERS
            # -------------------------

            if source == "TimesOfIndia":
                if "articleshow" in href:
                    links.add(href)

            elif source == "IndianExpressCrime":
                if "/article/" in href:
                    links.add(href)

            elif source == "TheHinduNational":
                if "/news/" in href:
                    links.add(href)

            elif source == "HindustanTimesCrime":
                if "/india-news/" in href or "/cities/" in href:
                    links.add(href)

            elif source == "NDTV":
                if "/india-news/" in href:
                    links.add(href)

            elif source == "IndiaToday":
                if "/story/" in href:
                    links.add(href)

            elif source == "ThePrint":
                if "/india/" in href or "/crime/" in href:
                    links.add(href)

            elif source == "ScrollCrime":
                if "/article/" in href:
                    links.add(href)

            elif source == "News18":
                if "/news/" in href:
                    links.add(href)

            elif source == "DeccanHeraldCrime":
                if "/india/" in href or "/crime/" in href:
                    links.add(href)

            elif source == "FreePressJournal":
                if "/crime/" in href:
                    links.add(href)

            elif source == "DeccanChronicle":
                if "/nation/" in href:
                    links.add(href)

            elif source == "TimesNowCrime":
                if "/crime/" in href:
                    links.add(href)

            elif source == "TribuneIndia":
                if "/news/" in href:
                    links.add(href)

            else:
                if "/crime" in href or "/india" in href:
                    links.add(href)

        return list(links)

    except:

        return []


# =========================================
# ARTICLE CONTENT EXTRACTION
# =========================================

def extract_article_content(url):

    try:

        r = requests.get(url, headers=HEADERS, timeout=15)

        soup = BeautifulSoup(r.text, "html.parser")


        # -------------------------
        # TITLE
        # -------------------------

        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else ""


        # -------------------------
        # TEXT
        # -------------------------

        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text(strip=True) for p in paragraphs)


        # -------------------------
        # DATE EXTRACTION
        # -------------------------

        publish_date = None

        # JSON-LD method
        scripts = soup.find_all("script", type="application/ld+json")

        for script in scripts:

            try:

                data = json.loads(script.string)

                if isinstance(data, dict):

                    if "datePublished" in data:
                        publish_date = data["datePublished"]
                        break

                if isinstance(data, list):

                    for item in data:
                        if "datePublished" in item:
                            publish_date = item["datePublished"]
                            break

            except:
                pass


        # OpenGraph fallback
        if publish_date is None:

            og = soup.find("meta", property="article:published_time")

            if og and og.get("content"):
                publish_date = og["content"]


        # time tag fallback
        if publish_date is None:

            time_tag = soup.find("time")

            if time_tag:
                publish_date = time_tag.get_text(strip=True)


        # URL fallback
        if publish_date is None:

            match = re.search(
                r"/(202[3-6])/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/",
                url
            )

            if match:
                publish_date = "-".join(match.groups())


        return title, text, publish_date


    except:

        return "", "", None


# =========================================
# MAIN SCRAPER
# =========================================

def scrape_articles():

    rows = []

    for source, pages in NEWS_SOURCES.items():

        print("\nScraping source:", source)

        all_links = set()

        for base_url in pages:

            for page in range(1, 30):

                page_url = base_url.format(page)

                links = get_article_links(page_url, source)

                all_links.update(links)

        print("Total article links collected:", len(all_links))


        for url in tqdm(all_links):

            title, text, publish_date = extract_article_content(url)

            if not title or not text:
                continue

            rows.append({

                "source": source,
                "url": url,
                "title": title,
                "text": text,
                "publish_date": publish_date

            })


    df = pd.DataFrame(rows)

    df.to_csv(RAW_FILE, index=False)

    print("\nRaw dataset saved:", RAW_FILE)