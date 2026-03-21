HEADERS = {"User-Agent": "Mozilla/5.0"}

RAW_FILE = "scraped_articles_raw.csv"
PROCESSED_FILE = "crime_articles_dataset.csv"
CITY_FILE = "city_risk_dataset.csv"

NEWS_SOURCES = {

"TimesOfIndia":[
"https://timesofindia.indiatimes.com/topic/rape/news?page={}",
"https://timesofindia.indiatimes.com/topic/sexual-assault/news?page={}",
"https://timesofindia.indiatimes.com/topic/crime/news?page={}"
],

"TheHinduNational":[
"https://www.thehindu.com/news/national/?page={}",
"https://www.thehindu.com/news/cities/?page={}"
],

"HindustanTimesCrime":[
"https://www.hindustantimes.com/topic/crime/page-{}",
"https://www.hindustantimes.com/india-news/page-{}"
],

"IndianExpressCrime":[
"https://indianexpress.com/section/crime/page/{}"
],

"AsianAgeNews":[
"https://www.asianage.com/?page={}",
"https://www.asianage.com/india/crime?page={}"
],

"DeccanHeraldCrime":[
"https://www.deccanherald.com/tag/crime?page={}",
"https://www.deccanherald.com/india-crime?page={}"
],

"TheWeekNews":[
"https://www.theweek.in/news.html?page={}",
"https://www.theweek.in/news/india.html?page={}"
],

"ScrollCrime":[
"https://scroll.in/tag/crime?page={}"
],

"NDTV":[
"https://www.ndtv.com/topic/india-crime-news?page={}"
],

"News18":[
"https://www.news18.com/topics/india-crime/?page={}",
"https://www.news18.com/topics/crime/?page={}"
],

"TheIndiaWire":[
"https://theindiawire.com/category/crime/page/{}"
],

"FreePressJournal":[
"https://www.freepressjournal.in/crime-news?page={}"
],

"IndiaToday":[
"https://www.indiatoday.in/crime?page={}"
],

"ThePrint":[
"https://theprint.in/tag/crime-in-india/page/{}"
],

"TribuneIndia":[
"https://www.tribuneindia.com/topic/indian-crime-news?page={}"
],

"HansIndia":[
"https://www.thehansindia.com/tags/India-crime-news?page={}"
],

"DeccanChronicle":[
"https://www.deccanchronicle.com/nation/crime?page={}"
],

"TimesNowCrime":[
"https://www.timesnownews.com/crime?page={}"
],

"NationalHeraldCrime":[
"https://www.nationalheraldindia.com/section/crime?page={}"
],

"WerIndiaCrime":[
"https://werindia.com/crime-and-justice?page={}"
],

"DNAIndia":[
"https://www.dnaindia.com/india?page={}"
]

}



#scrapper



# =========================================
# IMPORT LIBRARIES
# =========================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import re

from config import HEADERS, NEWS_SOURCES, RAW_FILE


# =========================================
# LINK EXTRACTION
# =========================================

def get_article_links(page_url):

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

            if href.startswith("http") and len(href) > 40:

                if not any(skip in href for skip in [
                    "facebook",
                    "twitter",
                    "instagram",
                    "youtube",
                    "mailto",
                    "#"
                ]):

                    links.add(href)

        return list(links)

    except:

        return []


# =========================================
# ARTICLE EXTRACTION
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

        date = None

        # 1️⃣ OpenGraph meta tag
        og_date = soup.find("meta", property="article:published_time")

        if og_date and og_date.get("content"):

            date = og_date["content"]


        # 2️⃣ meta pubdate
        if date is None:

            meta_pub = soup.find("meta", {"name": "pubdate"})

            if meta_pub and meta_pub.get("content"):

                date = meta_pub["content"]


        # 3️⃣ time tag
        if date is None:

            time_tag = soup.find("time")

            if time_tag:

                raw_date = time_tag.get_text()

                raw_date = raw_date.replace("IST", "").strip()

                date = raw_date


        # 4️⃣ extract date from URL
        if date is None:

            match = re.search(
                r"/(202[3-6])/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/",
                url
            )

            if match:

                date = "-".join(match.groups())


        return title, text, date


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

                links = get_article_links(page_url)

                all_links.update(links)

        print("Total links collected:", len(all_links))


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