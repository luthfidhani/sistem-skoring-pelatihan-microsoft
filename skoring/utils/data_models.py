import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
experience_dir = os.path.abspath(os.path.join(base_dir, "datasets/Experience.xlsx"))
catalog_train = os.path.abspath(os.path.join(base_dir, "datasets/TrainingCatalog.xlsx"))


def save(dir, data): #function untuk saving experience / catalog
    data = pd.DataFrame([{"data": data}]) # menjadikan data sebagai dataframe
    workbook = load_workbook(filename=dir) # open excel
    worksheet = workbook["Sheet1"] # ambil data sheet1
    for r in dataframe_to_rows(data, index=False, header=False):
        worksheet.append(r)
    workbook.save(dir) #simpan data ke excel


def add_experience(data):
    save(experience_dir, data)


def add_training_catalog(data):
    save(catalog_train, data)
