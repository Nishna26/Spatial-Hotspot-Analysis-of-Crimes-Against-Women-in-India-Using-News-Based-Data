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