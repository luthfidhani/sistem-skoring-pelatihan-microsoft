import os
import httpx
import asyncio
import tweepy
import numpy as np # import library numpy untuk perhitungan matematika
import pandas as pd # import library pandas untuk membaca data 
from pytrends.request import TrendReq #import library google trend api
from sklearn.feature_extraction.text import TfidfVectorizer # import library tfidf dari sklearn untuk menghitung tf-idf dari data
from sklearn.metrics.pairwise import cosine_similarity # import library cosin similarity dari sklearn untuk menghitung cosine similaroty
from django.conf import settings

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__))) # mendapatkan base direcrtory dari project ini
path_event_detail = os.path.abspath(os.path.join(base_dir, "datasets/Event Details.xlsx")) # join bash dir dengan dataset dir file
path_training_catalog = os.path.abspath(os.path.join(base_dir, "datasets/Training Catalog.xlsx")) # join bash dir dengan dataset dir file

client = tweepy.Client(bearer_token=settings.BEARER_TOKEN)

def read_data_source():
    df_event_detail = pd.read_excel(path_event_detail).dropna(axis=0) #membuka file excel Event Details.xlsx
    tittle_event_detail = np.array(df_event_detail)[:,0] # mengambil kolom tittle dan dijadikan array 
    learning_outcome_event_detail = [event_detail.replace('\xa0','') for event_detail in np.array(df_event_detail)[:,1]] #menjadikan dataframe ke array dan menghapus karakter \xa0


    df_training_catalog = pd.read_excel(path_training_catalog).dropna(axis=0) #membuka file excel Event Details.xlsx
    tittle_training_catalog = np.array(df_training_catalog)[:,0] # mengambil kolom tittle dan dijadikan array 
    learning_outcome_training_catalog = np.array(df_training_catalog)[:,1] # mengambil kolom learning outcome dan dijadikan array

    return [learning_outcome_event_detail, learning_outcome_training_catalog], [tittle_event_detail, tittle_training_catalog]

#fungsi untuk melakukan http requests
async def request_worker(url, json, headers):
    client = httpx.AsyncClient() # inisialisasi client
    response = await client.post(url=url, json=json, headers=headers) #request ke server
    return response.json() # retusn as a json

async def get_eventbrite_value(topics):
    url = "https://www.eventbrite.com/api/v3/destination/search/"
    headers = {
        "Cookie": f"csrftoken={settings.CSRFTOKEN}",
        "Referer": "https://www.eventbrite.com/d/indonesia",
        "X-CSRFToken": f"{settings.CSRFTOKEN}",
    }

    tasks = []
    for topic in topics:
        payload = {
            "event_search": {
                "q":topic,
                "dates":"current_future",
                "dedup":True,
                "places":["85632203"], # Indoneisa
                "page":1,
                "page_size":100,
                "online_events_only":False,
                "include_promoted_events":True
            }
        }
        tasks.append(asyncio.ensure_future(request_worker(url=url, json=payload, headers=headers))) # mengeksekusi request worker secara async
    responses = await asyncio.gather(*tasks) # menkoleksi responses
    values = np.array([data.get("events").get("pagination").get("object_count") for data in responses]) # mengumpulkan nilai dari dari bbrpa response menjadi 1 list
    limit_values = np.array([value if value <= 15 else 15 for value in values]) # melimit value max 15

    return values, limit_values * 0.067 #mereturn jumlah event di eventbrite dan limit value dengan dikali dengan 0.067

async def get_tweet_count(topic):
    return client.get_recent_tweets_count(query=topic, granularity='day') # proses untuk mendapatkan nilai dari twitter


async def get_trending_value(topics):
    tasks = [asyncio.create_task(get_tweet_count(query)) for query in topics] # mengeksekusi get_tweet_count secara async dan dijadikan 1 list hasilnya
    responses = await asyncio.gather(*tasks) # mengkoleksi responses
    value = (sum([response.meta.get("total_tweet_count") if response.meta.get("total_tweet_count") <= 10000 else 10000 for response in responses])/len(topics)) / 10000 # perhitungan nilai jika nilai diatas 10000 maka dilimit menjadi 10000. kemudian diambil rata-rata dan dibagi 10000
    results = []
    for i in range(len(topics)):
        results.append(
            {
                "topic": topics[i],
                "data": responses[i].data,
                "total_tweet_count": responses[i].meta.get("total_tweet_count")
            }
        ) # hasil dari get_tweet_Count dijadikan dict agar mudah di integrasikan di django templates
    return value, results


def get_cosim_value(learning_outcomes, tittle, query, threshold=0.2): # function cosim dengan parameter corpus dan query
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2)) # inisialisasi obyek tfidf dengan parameter stopword english dan ngram 1 dan 2

    tfidf_learning_outcomes = vectorizer.fit_transform(learning_outcomes) # melakukan pembobotan kata korpus
    tfidf_query = vectorizer.transform([query]) # melakukan pembobotan query dengan data tf-idf dari learning_outcomes

    value_cosims = cosine_similarity(tfidf_query, tfidf_learning_outcomes).flatten() #melakukan perhitungan cosine similarity kemudian dijadikan array 1 dimensi

    value_learning_outcomes = [value for value in value_cosims if value >= threshold] # menfilter nilai value_cosims lebih >= threshold
    index_learning_outcomes = np.where(value_cosims >= threshold) # mencari index yang value_cosims >= threshold
    selected_tittle = [tittle[index] for index in index_learning_outcomes][0] # mencari event yang terdapat pada index_learning_outcomes

    results = pd.DataFrame( # tittle dan value dijadikan dataframe
        {
            "tittle": selected_tittle,
            "values": value_learning_outcomes,
        }
    ).groupby('tittle')['values'].sum() # menjumlahkan value berdasarkan nilai unik dari tittle

    # print(index_learning_outcomes)
    # print(value_learning_outcomes)
    # print([learning_outcomes[index] for index in index_learning_outcomes[0]])

    tittle = np.array(list(results.to_dict().keys())) #mengambil kolom title untuk dijadikan array
    tittle = tittle.reshape(len(tittle), 1) # dari ['title1', 'title2', 'title3'] => [['title1'], ['title2'], ['title3'],] agar mudah gabung secara horisontal dengan values nya

    values = np.array(results.values)
    values = values.reshape(len(values), 1) # dari ['value1', 'value2', 'value3'] => [['value1'], ['value2'], ['value3'],] agar mudah gabung secara horisontal dengan tittle nya

    return np.hstack((tittle, values)), np.mean(results.values) # return ([unique_tittle, value_tittle]), mean

def train(query, topics):
    topics = topics.split(",") # split topic dengan pemisah ,
    learning_outcomes, tittle = read_data_source()

    data_cosims = []
    mean_cosims = []
    for i in range(len(learning_outcomes)): #melakukan perulangan dari list learning_outcomes
        cosims, mean = get_cosim_value(learning_outcomes[i], tittle[i], query) #melakukan perhitungan cosim value
        data_cosims.append(cosims) # menggabung nilai cosim pada setiap perulangan
        mean_cosims.append(mean) # menggabung nilai mean pada setiap perulangan

    number_of_eventbrite, eventbrite_value = asyncio.run(get_eventbrite_value(topics)) # request value from eventbrite using async method based on topics
    trending_value, data_trending = asyncio.run(get_trending_value(topics))
    
    # values = [event details, training catalog, trending value, event brite value]
    bobot = np.array([4, 4, 2, 2])
    values = [mean_cosims[0], mean_cosims[1], trending_value, eventbrite_value.mean()] # menggabung kan menjadi 1 list
    values = np.nan_to_num(values) * bobot # convert NaN value to 0 dan dikali dengan bobotnya

    # membatasi values dengan max bobot
    for i in range(len(values)):
        values[i] = values[i] if values[i] <= bobot[i] else bobot[i]

    return np.sum(values), values, data_cosims, mean_cosims, number_of_eventbrite, data_trending # mengembalikan jumlah dari rata-rata
