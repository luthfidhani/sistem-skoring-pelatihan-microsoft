import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from .ai_models import path_event_detail, path_training_catalog


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
