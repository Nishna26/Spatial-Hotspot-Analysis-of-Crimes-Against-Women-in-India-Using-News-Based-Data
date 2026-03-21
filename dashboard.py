import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Women Crime Risk Dashboard",
    layout="wide"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>

.main-header {
    text-align: center;
    font-size: 50px;
    font-weight: 800;
    background: linear-gradient(90deg,#ff4b4b,#ff7a18);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 30px;
}

.metric-card {
    background-color: #f8f9fa;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
}

.metric-value {
    font-size: 42px;
    font-weight: 700;
    color: #2c3e50;
}

.metric-label {
    font-size: 18px;
    color: #7f8c8d;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# HEADER
# =====================================

st.markdown(
'<div class="main-header">Women Crime Risk Dashboard</div>',
unsafe_allow_html=True
)


# =====================================
# LOAD DATA
# =====================================

crime_df = pd.read_csv("crime_articles_dataset.csv")
city_df = pd.read_csv("city_risk_dataset_cleaned.csv")

crime_df["publish_date"] = pd.to_datetime(
    crime_df["publish_date"],
    errors="coerce"
)


# =====================================
# FILTERS
# =====================================

st.sidebar.title("Filters")

cities = st.sidebar.multiselect(
    "Select Cities",
    sorted(crime_df["primary_location"].dropna().unique())
)

severity_filter = st.sidebar.slider(
    "Minimum Severity",
    1,
    3,
    1
)

filtered_df = crime_df.copy()

if cities:
    filtered_df = filtered_df[
        filtered_df["primary_location"].isin(cities)
    ]

filtered_df = filtered_df[
    filtered_df["severity"] >= severity_filter
]


# =====================================
# METRICS
# =====================================

total_articles = len(filtered_df)
total_cities = filtered_df["primary_location"].nunique()
avg_severity = filtered_df["severity"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Crime Articles</div>
        <div class="metric-value">{total_articles}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Cities Detected</div>
        <div class="metric-value">{total_cities}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Average Severity</div>
        <div class="metric-value">{round(avg_severity,2)}</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================
# MAP
# =====================================

st.markdown(
'<div class="section-title">Crime Hotspot Map</div>',
unsafe_allow_html=True
)

m = folium.Map(
    location=[22.97,78.65],
    zoom_start=5,
    tiles="CartoDB positron"
)

for _, row in city_df.iterrows():

    if pd.notna(row["lat"]):

        popup_html = f"""
        <b>{row['primary_location']}</b><br>
        Total Cases: {row['total_cases']}<br>
        Risk Score: {round(row['normalized_risk'],2)}<br><br>

        <b>Need Help?</b><br>
        <a href="https://www.google.com/search?q={row['primary_location']}+women+helpline+number"
        target="_blank">
        Find Helpline Numbers
        </a>
        """

        folium.CircleMarker(
            location=[row["lat"],row["lon"]],
            radius=max(5,row["normalized_risk"]*20),
            popup=folium.Popup(popup_html,max_width=300),
            color="red",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

st_folium(m,width=1200,height=500)


# =====================================
# TOP RISK CITIES
# =====================================

st.markdown(
'<div class="section-title">Top Risk Cities</div>',
unsafe_allow_html=True
)

top_cities = city_df.sort_values(
    "normalized_risk",
    ascending=False
).head(10)

st.dataframe(top_cities,use_container_width=True)


# =====================================
# SEVERITY DISTRIBUTION
# =====================================

st.markdown(
'<div class="section-title">Crime Severity Distribution</div>',
unsafe_allow_html=True
)

fig = px.histogram(
    filtered_df,
    x="severity",
    nbins=3,
    color="severity",
    color_discrete_sequence=["#ff4b4b","#ff7a18","#ffa600"]
)

fig.update_layout(
    xaxis_title="Severity Level",
    yaxis_title="Number of Cases"
)

st.plotly_chart(fig,use_container_width=True)


# =====================================
# CRIME TREND OVER TIME
# =====================================

st.markdown(
'<div class="section-title">Crime Trends Over Time</div>',
unsafe_allow_html=True
)

trend = (
    filtered_df
    .groupby(filtered_df["publish_date"].dt.date)
    .size()
    .reset_index(name="cases")
)

fig = px.line(
    trend,
    x="publish_date",
    y="cases",
    markers=True,
    color_discrete_sequence=["#ff4b4b"]
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Number of Cases"
)

st.plotly_chart(fig,use_container_width=True)


# =====================================
# MOST AFFECTED CITIES
# =====================================

st.markdown(
'<div class="section-title">Most Affected Cities</div>',
unsafe_allow_html=True
)

EXCLUDE_LOCATIONS = [
"india",
"uttar pradesh",
"madhya pradesh",
"west bengal",
"rajasthan",
"gujarat",
"telangana",
"odisha",
"bihar",
"haryana",
"karnataka",
"kerala"
]

city_counts = (
    filtered_df[
        ~filtered_df["primary_location"].str.lower().isin(EXCLUDE_LOCATIONS)
    ]
    ["primary_location"]
    .value_counts()
    .head(10)
    .reset_index()
)

city_counts.columns = ["City","Cases"]

fig = px.bar(
    city_counts,
    x="City",
    y="Cases",
    color="Cases",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig,use_container_width=True)


