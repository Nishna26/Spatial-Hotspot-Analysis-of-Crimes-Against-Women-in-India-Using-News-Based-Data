FEMALE_KEYWORDS = [
"woman","women","girl","girls","minor girl",
"schoolgirl","college girl","young woman",
"elderly woman","she was","she had","she alleged","her"
]

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
"dowry","family dispute","marital dispute"
]


def is_women_related(text):

    text = text.lower()

    return any(k in text for k in FEMALE_KEYWORDS)


def is_crime_against_women(text):

    text = text.lower()

    if any(x in text for x in EXCLUDE_DOMESTIC):
        return False

    return any(x in text for x in CRIME_KEYWORDS)