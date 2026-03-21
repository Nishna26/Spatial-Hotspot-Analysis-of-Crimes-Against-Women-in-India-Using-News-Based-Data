# =========================================
# IMPORT LIBRARIES
# =========================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import numpy as np
import os
import re
import time
import spacy
from geopy.geocoders import Nominatim


# =========================================
# FILE PATHS
# =========================================

RAW_FILE = "scraped_articles_raw.csv"
PROCESSED_FILE = "crime_articles_dataset.csv"
CITY_FILE = "city_risk_dataset.csv"

HEADERS = {"User-Agent": "Mozilla/5.0"}

END_DATE = pd.Timestamp.now().tz_localize(None)


# =========================================
# LOAD NLP
# =========================================

nlp = spacy.load("en_core_web_sm")


# =========================================
# FEMALE KEYWORDS
# =========================================

FEMALE_KEYWORDS = [
"woman","women","girl","girls","minor girl",
"schoolgirl","college girl","young woman",
"elderly woman","she was","she had","she alleged","her"
]

def is_women_related(text):

    text = text.lower()

    return any(kw in text for kw in FEMALE_KEYWORDS)


# =========================================
# CRIME KEYWORDS
# =========================================

CRIME_KEYWORDS = [
"rape","raped","gang rape",
"sexual assault","attempt to rape",
"molest","molested","molestation","groped",
"harass","harassed","harassment",
"eve teasing","stalking","stalked",
"assaulted","attack","attacked",
"abduction","kidnapped",
"acid attack","acid thrown"
]

EXCLUDE_DOMESTIC = [
"domestic violence","husband","in-laws",
"dowry","family dispute","marital dispute","spousal abuse"
]

def is_crime_against_women(text):

    text = text.lower()

    if any(bad in text for bad in EXCLUDE_DOMESTIC):
        return False

    return any(kw in text for kw in CRIME_KEYWORDS)


# =========================================
# NEWS SOURCES
# =========================================

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

            if href.startswith("/"):

                base = page_url.split("/")[0] + "//" + page_url.split("/")[2]

                href = base + href

            if href.startswith("http") and len(href) > 40:

                if not any(skip in href for skip in [
                    "facebook","twitter","instagram","youtube","mailto","#"
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

        title_tag = soup.find("h1")

        title = title_tag.get_text(strip=True) if title_tag else ""

        paragraphs = soup.find_all("p")

        text = " ".join(p.get_text(strip=True) for p in paragraphs)

        date = None

        og_date = soup.find("meta", property="article:published_time")

        if og_date and og_date.get("content"):

            date = pd.to_datetime(og_date["content"], errors="coerce")

        if pd.notna(date):

            date = date.tz_localize(None)

        return title, text, date

    except:

        return "", "", None


# =========================================
# SCRAPER
# =========================================

def scrape_articles():

    rows = []

    for source, pages in NEWS_SOURCES.items():

        print("Scraping:", source)

        links = set()

        for base_url in pages:

            for page in range(1,30):

                page_url = base_url.format(page)

                links.update(get_article_links(page_url))

        for url in tqdm(links):

            title, text, publish_date = extract_article_content(url)

            if not title or not text:
                continue

            rows.append({

                "source":source,
                "url":url,
                "title":title,
                "text":text,
                "publish_date":publish_date

            })

    df = pd.DataFrame(rows)

    df.to_csv(RAW_FILE, index=False)

    print("Raw data saved:", RAW_FILE)


# =========================================
# LOCATION EXTRACTION
# =========================================

def extract_primary_location(text):

    doc = nlp(text)

    loc_freq = {}

    for ent in doc.ents:

        if ent.label_ == "GPE":

            loc = ent.text

            loc_freq[loc] = loc_freq.get(loc,0)+1

    if loc_freq:

        return max(loc_freq,key=loc_freq.get)

    return None


# =========================================
# SEVERITY
# =========================================

def assign_severity(text):

    text = text.lower()

    if "rape" in text:
        return 3

    if "molest" in text or "assault" in text:
        return 2

    return 1


# =========================================
# RECENCY WEIGHT
# =========================================

def recency_weight(date):

    if pd.isna(date):
        return 0.25

    days_old = (pd.Timestamp.now() - date).days

    return max(0.1, np.exp(-0.002 * days_old))


# =========================================
# PROCESS DATASET
# =========================================

def process_dataset():

    df = pd.read_csv(RAW_FILE)

    df["combined_text"] = df["title"].fillna("") + " " + df["text"].fillna("")

    df = df[df["combined_text"].apply(is_women_related)]

    df = df[df["combined_text"].apply(is_crime_against_women)]

    df["publish_date"] = pd.to_datetime(df["publish_date"], errors="coerce")

    df["primary_location"] = df["combined_text"].apply(extract_primary_location)

    df["severity"] = df["combined_text"].apply(assign_severity)

    df["recency_weight"] = df["publish_date"].apply(recency_weight)

    df["risk_score"] = df["severity"] * df["recency_weight"]

    df.to_csv(PROCESSED_FILE, index=False)

    print("Processed dataset saved:", PROCESSED_FILE)

    return df


# =========================================
# CITY RISK
# =========================================

def compute_city_risk(df):

    city_risk = (

        df.groupby("primary_location")

        .agg(

            total_cases=("risk_score","count"),
            avg_severity=("severity","mean"),
            avg_recency=("recency_weight","mean"),
            total_risk=("risk_score","sum")

        )

    )

    city_risk["normalized_risk"] = city_risk["total_risk"] / city_risk["total_cases"]

    geolocator = Nominatim(user_agent="crime_map")

    def get_coordinates(city):

        try:

            loc = geolocator.geocode(city + ", India")

            if loc:

                return pd.Series([loc.latitude, loc.longitude])

        except:

            pass

        return pd.Series([None,None])

    city_risk = city_risk.reset_index()

    city_risk[["lat","lon"]] = city_risk["primary_location"].apply(get_coordinates)

    city_risk.to_csv(CITY_FILE, index=False)

    print("City risk dataset saved:", CITY_FILE)


# =========================================
# MAIN PIPELINE
# =========================================

def run_pipeline():

    choice = input("Scrape new articles? (y/n): ")

    if choice == "y":

        scrape_articles()

    df = process_dataset()

    compute_city_risk(df)


# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    run_pipeline()