# To Run Pipeline -->
# C:\Users\NISHNA\anaconda3\python.exe main.py
import pandas as pd
from tqdm import tqdm

from scraper import scrape_articles
from processor import process_dataset
from risk_model import assign_severity, recency_weight
from geocoder import get_coordinates
from config import CITY_FILE


# =====================================
# PIPELINE
# =====================================

def run_pipeline():

    print("\n================================")
    print("CRIME ANALYTICS PIPELINE STARTED")
    print("================================\n")

    # --------------------------------
    # STEP 1: SCRAPING
    # --------------------------------

    choice = input("Step 1: Scrape new articles? (y/n): ")

    if choice.lower() == "y":

        print("\n[STEP 1] Scraping articles...\n")

        scrape_articles()

        print("\n[STEP 1 COMPLETE]\n")

    else:

        print("\n[STEP 1 SKIPPED] Using existing raw dataset\n")


    # --------------------------------
    # STEP 2: PROCESS RAW DATA
    # --------------------------------

    print("[STEP 2] Processing raw dataset...\n")

    df = process_dataset()

    print("Rows after filtering:", len(df))

    print("\n[STEP 2 COMPLETE]\n")


    # --------------------------------
    # CLEAN ANY CORRUPTED COLUMNS
    # --------------------------------

    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]


    # --------------------------------
    # STEP 3: SEVERITY CALCULATION
    # --------------------------------

    print("[STEP 3] Assigning severity scores...\n")

    df["severity"] = df["combined_text"].apply(assign_severity)

    print("Severity assigned.")


    # --------------------------------
    # STEP 4: DATE CLEANING
    # --------------------------------

    print("\n[STEP 4] Cleaning publish dates...\n")

    df["publish_date"] = pd.to_datetime(
        df["publish_date"],
        errors="coerce",
        utc=True
    ).dt.tz_convert(None)

    print("Dates cleaned.")


    # --------------------------------
    # STEP 5: RECENCY WEIGHT
    # --------------------------------

    print("\n[STEP 5] Calculating recency weights...\n")

    df["recency_weight"] = df["publish_date"].apply(recency_weight)

    print("Recency weights calculated.")


    # --------------------------------
    # STEP 6: RISK SCORE
    # --------------------------------

    print("\n[STEP 6] Computing risk scores...\n")

    df["risk_score"] = df["severity"] * df["recency_weight"]

    print("Risk scores computed.")


    # --------------------------------
    # VALIDATE DATASET STRUCTURE
    # --------------------------------

    required_columns = [
        "source",
        "url",
        "title",
        "text",
        "publish_date",
        "combined_text",
        "primary_location",
        "severity",
        "recency_weight",
        "risk_score"
    ]

    missing_cols = [c for c in required_columns if c not in df.columns]

    if missing_cols:

        raise ValueError(
            f"Dataset missing required columns: {missing_cols}"
        )


    # --------------------------------
    # SAVE CLEAN ARTICLE DATASET
    # --------------------------------

    print("\nSaving processed article dataset...\n")

    df = df[required_columns]

    df.to_csv(
        "crime_articles_dataset.csv",
        index=False,
        encoding="utf-8"
    )

    print("Saved: crime_articles_dataset.csv")


    # --------------------------------
    # STEP 7: CITY RISK AGGREGATION
    # --------------------------------

    print("\n[STEP 7] Aggregating city risk...\n")

    city_risk = (

        df.groupby("primary_location")

        .agg(

            total_cases=("risk_score", "count"),
            avg_severity=("severity", "mean"),
            avg_recency=("recency_weight", "mean"),
            total_risk=("risk_score", "sum")

        )

    )

    city_risk["normalized_risk"] = (

        city_risk["total_risk"] /
        city_risk["total_cases"]

    )

    city_risk = city_risk.reset_index()

    print("City risk dataset created.")


    # --------------------------------
    # STEP 8: GEOCODING (FAST)
    # --------------------------------

    print("\n[STEP 8] Fetching city coordinates...\n")

    unique_cities = city_risk["primary_location"].dropna().unique()

    coords = {}

    for city in tqdm(unique_cities):

        latlon = get_coordinates(city)

        coords[city] = latlon


    city_risk["lat"] = city_risk["primary_location"].map(

        lambda x: coords.get(x, [None, None])[0]

    )

    city_risk["lon"] = city_risk["primary_location"].map(

        lambda x: coords.get(x, [None, None])[1]

    )

    print("Geocoding complete.")


    # --------------------------------
    # STEP 9: SAVE CITY DATASET
    # --------------------------------

    print("\n[STEP 9] Saving city dataset...\n")

    city_risk.to_csv(
        CITY_FILE,
        index=False,
        encoding="utf-8"
    )

    print("Saved:", CITY_FILE)


    print("\n================================")
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("================================\n")


# =====================================
# RUN PIPELINE
# =====================================

if __name__ == "__main__":

    run_pipeline()