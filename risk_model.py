import pandas as pd
import numpy as np


def assign_severity(text):

    text = text.lower()

    if "rape" in text:
        return 3

    if "assault" in text or "molest" in text:
        return 2

    return 1


def recency_weight(date):

    if pd.isna(date):
        return 0.25

    days_old = (pd.Timestamp.now() - date).days

    return max(0.1, np.exp(-0.002 * days_old))