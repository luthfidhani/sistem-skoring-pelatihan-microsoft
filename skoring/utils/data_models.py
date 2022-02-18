import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
experience_dir = os.path.abspath(os.path.join(base_dir, "datasets/Experience.xlsx"))
catalog_train = os.path.abspath(os.path.join(base_dir, "datasets/TrainingCatalog.xlsx"))


def save(dir, data):
    data = pd.DataFrame([{"data": data}])
    wb = load_workbook(filename=dir)
    ws = wb["Sheet1"]
    for r in dataframe_to_rows(data, index=False, header=False):
        ws.append(r)
    wb.save(dir)


def add_experience(data):
    save(experience_dir, data)


def add_training_catalog(data):
    save(catalog_train, data)
