from geopy.geocoders import Nominatim
import pandas as pd


geolocator = Nominatim(user_agent="crime_map")


def get_coordinates(city):

    try:

        loc = geolocator.geocode(city + ", India")

        if loc:

            return pd.Series([loc.latitude, loc.longitude])

    except:

        pass

    return pd.Series([None,None])