import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from .ai_models import path_event_detail, path_training_catalog

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__))) # mendapatkan base direcrtory dari project ini
path_result_history = os.path.abspath(os.path.join(base_dir, "datasets/Result History.xlsx")) # join bash dir dengan dataset dir file


def save_to_excel(dir, data): #function untuk saving experience / catalog
    workbook = load_workbook(filename=dir) # open excel
    worksheet = workbook["Sheet1"] # ambil data sheet1
    for r in dataframe_to_rows(data, index=False, header=False):
        worksheet.append(r)
    workbook.save(dir) #simpan data ke excel


def convert_to_dataframe(tittle, learning_outcomes):
    learning_outcomes = learning_outcomes.splitlines() # split /n (enter)
    tittles = [tittle] * len(learning_outcomes) # menyamakan dimensi tittle dengan learning outcomes

    return pd.DataFrame(
        {
            "Tittle": tittles,
            "Learnng Outcome": learning_outcomes,
        }
    ) # mereturn sebagai dataframe

def add_event_detail(tittle, learning_outcomes):
    data = convert_to_dataframe(tittle, learning_outcomes) # melakukan convert ke dataframe
    save_to_excel(path_event_detail, data) # menyimpan data ke excel


def add_training_catalog(tittle, learning_outcomes):
    data = convert_to_dataframe(tittle, learning_outcomes) # melakukan convert ke dataframe
    save_to_excel(path_training_catalog, data) # menyimpan data ke excel


def add_result_history(data):

    # Menformat data treding twitter untuk digabungkan dengan result
    df = pd.DataFrame(columns=['topic', 'start_date', 'end_date', 'tweet_count'])
    for item in data.get("data_trending"):    
        # Loop through each data point
        i = 0
        for point in item['data']:       
            topic = "" if i > 0 else item['topic'] # untuk menformat topik agar di baris selanjutnya tidak ditampilkan "biar rapi". jika i > 0 maka diisi dengan string kosong
            df = pd.concat([df, pd.DataFrame({'topic': [topic], 'start_date': [point['start']], 'end_date': [point['end']], 'tweet_count': [point['tweet_count']]})], ignore_index=True)
            i += 1
        df = pd.concat([df, pd.DataFrame({'topic': "", 'start_date': "", 'end_date': "Total", 'tweet_count': [item["total_tweet_count"]]})], ignore_index=True) #menampilkan total count

    result = {
        "Query": [data.get("query")],
        "Topics": [data.get("topics")],
        "Hasil Event": [event[0] for event in data.get("cosim_data")[0]],
        "Skor Event": [event[1] for event in data.get("cosim_data")[0]],
        "Hasil Katalog": [event[0] for event in data.get("cosim_data")[1]],
        "Skor Katalog": [event[1] for event in data.get("cosim_data")[1]],
        "Hasil Eventbrite": data.get("topics").split(","),
        "Skor Eventbrite": data.get("number_of_eventbrite").tolist(),
        "Topik Twitter": df.get("topic").to_numpy(),
        "Start Date": df.get("start_date").to_numpy(),
        "End Date": df.get("end_date").to_numpy(),
        "Tweet Count": df.get("tweet_count").to_numpy(),
    }

    # Mendapatkan jumlah maksimum dari semua array
    max_len = max(len(result[key]) for key in result)

    # Mengisi setiap array dengan "" hingga panjangnya sama
    for key in result:
        if isinstance(result[key], list) and len(result[key]) < max_len:
            result[key].extend([""] * (max_len - len(result[key])))

    save_to_excel(path_result_history, pd.DataFrame(result)) # menyimpan data ke excel
