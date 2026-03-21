import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep

# load dataset
df = pd.read_csv("city_risk_dataset.csv")

geolocator = Nominatim(user_agent="crime_map")

def get_coords(city):

    try:

        location = geolocator.geocode(city + ", India", addressdetails=True)

        if location:

            address = location.raw.get("type","")

            if address in ["city","town","village","administrative"]:

                return location.latitude, location.longitude

    except:
        pass

    return None, None


for i, row in df.iterrows():

    if pd.isna(row["lat"]) or pd.isna(row["lon"]):

        city = row["primary_location"]

        lat, lon = get_coords(city)

        df.at[i, "lat"] = lat
        df.at[i, "lon"] = lon

        print("Fixed:", city)

        sleep(1)  # required for Nominatim rate limit


df.to_csv("city_risk_dataset.csv", index=False)

print("Coordinates updated.")