import os
import httpx
import asyncio
import numpy as np # import library numpy untuk perhitungan matematika
import pandas as pd # import library pandas untuk membaca data 
from pytrends.request import TrendReq #import library google trend api
from sklearn.feature_extraction.text import TfidfVectorizer # import library tfidf dari sklearn untuk menghitung tf-idf dari data
from sklearn.metrics.pairwise import cosine_similarity # import library cosin similarity dari sklearn untuk menghitung cosine similaroty

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__))) # mendapatkan base direcrtory dari project ini

path_event_detail = os.path.abspath(os.path.join(base_dir, "datasets/Event Details.xlsx")) # join bash dir dengan dataset dir file
df_event_detail = pd.read_excel(path_event_detail).dropna(axis=0) #membuka file excel Event Details.xlsx
events_event_detail = np.array(df_event_detail)[:,0]
learning_outcome_event_detail = [event_detail.replace('\xa0','') for event_detail in np.array(df_event_detail)[:,1]] #menjadikan dataframe ke array dan menghapus karakter \xa0


path_training_catalog = os.path.abspath(os.path.join(base_dir, "datasets/Training Catalog.xlsx")) # join bash dir dengan dataset dir file
df_training_catalog = pd.read_excel(path_training_catalog).dropna(axis=0) #membuka file excel Event Details.xlsx
events_training_catalog = np.array(df_training_catalog)[:,0]
learning_outcome_training_catalog = np.array(df_training_catalog)[:,1]


async def request_worker(url, json, headers):
    client = httpx.AsyncClient()
    response = await client.post(url=url, json=json, headers=headers)
    return response.json()

async def get_eventbrite_value(topics):
    url = "https://www.eventbrite.com/api/v3/destination/search/"
    headers = {
        "Cookie": "csrftoken=30307aa869a611eda80497a2ad387ead",
        "Referer": "https://www.eventbrite.com/d/indonesia",
        "X-CSRFToken": "30307aa869a611eda80497a2ad387ead",
    }

    tasks = []
    for topic in topics:
        payload = {
            "event_search": {
                "q":topic,
                "dates":"current_future",
                "dedup":True,
                "places":["85632203"],
                "page":1,
                "page_size":100,
                "online_events_only":False,
                "include_promoted_events":True
            }
        }
        tasks.append(asyncio.ensure_future(request_worker(url=url, json=payload, headers=headers)))
    responses = await asyncio.gather(*tasks)

    return np.mean(np.array([data.get("events").get("pagination").get("object_count") for data in responses])) / 10

def get_trending_value(topics):
    pytrend = TrendReq() #inisialisasi obyek google trend api
    pytrend.build_payload(kw_list=topics, cat=0, timeframe='today 12-m') # melakukan pencarian nilai dari query ke google trend api
    data = pytrend.interest_by_region() # melakukan pencarian by region

    return data.loc["Indonesia"].values.mean() / 10 # mengambil nilai dari negara indonesia kemudian dibagi dengan 10


def get_cosim_value(learning_outcomes, events, query, threshold=0.2): # function cosim dengan parameter corpus dan query
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2)) # inisialisasi obyek tfidf dengan parameter stopword english dan ngram 1 dan 2

    tfidf_learning_outcomes = vectorizer.fit_transform(learning_outcomes) # melakukan pembobotan kata korpus
    tfidf_query = vectorizer.transform([query]) # melakukan pembobotan query dengan data tf-idf dari learning_outcomes

    value_cosims = cosine_similarity(tfidf_query, tfidf_learning_outcomes).flatten() #melakukan perhitungan cosine similarity kemudian dijadikan array 1 dimensi
    cosim_sort = np.sort(value_cosims)[::-1] #melakukan pengurutan secara descending dari hasil cosine similarity
    
    value_learning_outcomes = [value for value in value_cosims if value >= threshold] # menfilter nilai value_cosims lebih >= threshold
    index_learning_outcomes = np.where(value_cosims >= threshold) # mencari index yang value_cosims >= threshold
    selected_events = [events[index] for index in index_learning_outcomes][0] # mencari event yang terdapat pada index_learning_outcomes
    
    results = pd.DataFrame( # events dan value dijadikan dataframe
        {
            "events": selected_events,
            "values": value_learning_outcomes,
        }
    ).groupby('events')['values'].sum() # menjumlahkan value berdasarkan nilai unik dari events

    events = np.array(list(results.to_dict().keys()))
    events = events.reshape(len(events), 1)

    values = np.array(results.values)
    values = values.reshape(len(values), 1)

    return np.hstack((events, values)), np.mean(results.values) # return ([unique_events, value_events]), mean

def train(query, topics):
    topics = topics.split(",")
    learning_outcomes = [learning_outcome_event_detail, learning_outcome_training_catalog]
    events = [events_event_detail, events_training_catalog]

    data_cosims = []
    mean_cosims = []
    for i in range(len(learning_outcomes)): #melakukan perulangan dari list learning_outcomes
        cosims, mean = get_cosim_value(learning_outcomes[i], events[i], query)
        data_cosims.append(cosims) #melakukan proses perhitungan cosim dengan memanggil fungsi cosim
        mean_cosims.append(mean)

    eventbrite_value = asyncio.run(get_eventbrite_value(topics)) # request value from eventbrite using async method based on topics
    trending_value = get_trending_value(topics) # request value from google trending based on topics
    
    # values = [event details, training catalog, trending value, event brite value]
    values = [mean_cosims[0], mean_cosims[1], trending_value, eventbrite_value]
    values = np.nan_to_num(values) * np.array([3, 3, 2, 2]) # convert NaN value to 0 dan dikali dengan bobotnya 

    return np.mean(values), values, data_cosims, mean_cosims # mengembalikan jumlah dari rata-rata
