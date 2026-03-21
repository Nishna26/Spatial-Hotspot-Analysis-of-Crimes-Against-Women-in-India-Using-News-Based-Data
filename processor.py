
import pandas as pd
import spacy
from config import RAW_FILE


# =========================================
# LOAD SPACY (NER ONLY → MUCH FASTER)
# =========================================

nlp = spacy.load(
    "en_core_web_sm",
    disable=["tagger", "parser", "lemmatizer"]
)


# =========================================
# FEMALE KEYWORDS
# =========================================

FEMALE_KEYWORDS = [
    "woman","women","girl","girls",
    "minor girl","schoolgirl",
    "college girl","young woman",
    "elderly woman","she was",
    "she had","she alleged","her"
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
    "molest","molested","molestation",
    "groped","harass","harassed",
    "harassment","eve teasing",
    "stalking","stalked",
    "assaulted","attack","attacked",
    "abduction","kidnapped",
    "acid attack","acid thrown"

]


EXCLUDE_DOMESTIC = [

    "domestic violence",
    "husband",
    "in-laws",
    "dowry",
    "family dispute",
    "marital dispute",
    "spousal abuse"

]


def is_crime_against_women(text):

    text = text.lower()

    if any(x in text for x in EXCLUDE_DOMESTIC):
        return False

    return any(kw in text for kw in CRIME_KEYWORDS)


# =========================================
# FAST LOCATION EXTRACTION
# =========================================

def extract_locations_batch(texts):

    locations = []

    docs = nlp.pipe(texts, batch_size=50)

    for doc in docs:

        loc_freq = {}

        for ent in doc.ents:

            if ent.label_ == "GPE":

                loc = ent.text

                loc_freq[loc] = loc_freq.get(loc, 0) + 1

        if loc_freq:

            locations.append(
                max(loc_freq, key=loc_freq.get)
            )

        else:

            locations.append(None)

    return locations


# =========================================
# LOCATION CLEANING
# =========================================

FOREIGN_LOCATIONS = [

    "Iran","US","U.S.","Israel","Oman",
    "Pakistan","Dubai","Turkey","Canada",
    "Russia","Bangladesh","UAE","China",
    "Afghanistan","Australia","France",
    "Germany","Saudi Arabia","Japan"

]


NON_LOCATION_WORDS = [

    "AI","Centre","Netflix","LinkedIn",
    "Suicide","Airport","Hindi",
    "Islam","Gang","Pocso"

]


NORMALIZATION_DICT = {

    "Bombay":"Mumbai",
    "New Delhi":"Delhi",
    "NEW DELHI":"Delhi",
    "Bengal":"West Bengal",
    "Andhra":"Andhra Pradesh"

}


def clean_location(loc):

    if pd.isna(loc):
        return None

    loc = loc.strip().title()

    if loc in FOREIGN_LOCATIONS:
        return None

    if loc in NON_LOCATION_WORDS:
        return None

    if loc in NORMALIZATION_DICT:
        return NORMALIZATION_DICT[loc]

    if len(loc) <= 2:
        return None

    return loc


# =========================================
# MAIN PROCESSOR
# =========================================

def process_dataset():

    print("Loading raw dataset...")

    df = pd.read_csv(

        RAW_FILE,
        engine="python",
        on_bad_lines="skip"

    )

    # remove corrupted columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]


    # -------------------------------------
    # CREATE COMBINED TEXT
    # -------------------------------------

    df["combined_text"] = (

        df["title"].fillna("") + " " +
        df["text"].fillna("")

    )


    # -------------------------------------
    # FILTER WOMEN ARTICLES
    # -------------------------------------

    print("Filtering women-related articles...")

    df = df[
        df["combined_text"].apply(is_women_related)
    ]


    # -------------------------------------
    # FILTER CRIME ARTICLES
    # -------------------------------------

    print("Filtering crime-related articles...")

    df = df[
        df["combined_text"].apply(is_crime_against_women)
    ]


    # -------------------------------------
    # REMOVE DUPLICATES
    # -------------------------------------

    df = df.drop_duplicates(subset=["title"])
    df = df.drop_duplicates(subset=["url"])


    # -------------------------------------
    # LOCATION EXTRACTION (FAST)
    # -------------------------------------

    print("Extracting locations (spaCy batch mode)...")

    df["primary_location"] = extract_locations_batch(

        df["combined_text"].fillna("")

    )


    # -------------------------------------
    # CLEAN LOCATIONS
    # -------------------------------------

    df["primary_location"] = df["primary_location"].apply(
        clean_location
    )


    df = df[
        df["primary_location"].notna()
    ]


    print("Dataset ready.")

    return df