import pandas as pd
import re

df = pd.read_csv("city_risk_dataset.csv")


# --------------------------------
# FOREIGN LOCATIONS
# --------------------------------

FOREIGN_LOCATIONS = {
"america","denmark","hungary","italy","nepal",
"new zealand","qatar","spain","texas",
"san francisco","portugal","jordan",
"tehran","turkmenistan","usa","uae", "rhode island","willington"
}


# --------------------------------
# NON LOCATION WORDS
# --------------------------------

NON_LOCATIONS = {
"burnt","farmland","livelihood","bollywood",
"covid-19","mahila","dalit","taj",
"crime","victim","accused","case",
"family","woman","girl","man","boy"
}


# --------------------------------
# NORMALIZATION RULES
# --------------------------------

NORMALIZATION = {

"north delhi":"Delhi",
"south delhi":"Delhi",
"east delhi":"Delhi",
"west delhi":"Delhi",

"vadodara city":"Vadodara",
"puri orissa":"Puri",

"haryana’s sirsa":"Sirsa",

"madhya pradesh’s":"Madhya Pradesh",
"madhya pradesh’s sehore":"Sehore",

"madras hc":"Chennai"
}


# --------------------------------
# CLEAN FUNCTION
# --------------------------------

def normalize_location(loc):

    if pd.isna(loc):
        return None

    loc = str(loc).strip()

    # remove encoding errors
    loc = loc.replace("â€™","").replace("’","")

    loc_lower = loc.lower()

    # remove foreign places
    if loc_lower in FOREIGN_LOCATIONS:
        return None

    # remove obvious non locations
    if loc_lower in NON_LOCATIONS:
        return None

    # apply normalization rules
    if loc_lower in NORMALIZATION:
        return NORMALIZATION[loc_lower]

    # remove numbers
    if re.search(r'\d', loc):
        return None

    # remove very short tokens
    if len(loc) <= 2:
        return None

    return loc.title()


df["primary_location"] = df["primary_location"].apply(normalize_location)

df = df[df["primary_location"].notna()]

# remove duplicates
df = df.drop_duplicates(subset=["primary_location"])


df.to_csv("city_risk_dataset_cleaned.csv", index=False)

print("Normalization complete")
print("Final number of locations:", len(df))