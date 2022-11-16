import os
import numpy as np # import library numpy untuk perhitungan matematika
import pandas as pd # import library pandas untuk membaca data 
from pytrends.request import TrendReq #import library google trend api
from sklearn.feature_extraction.text import TfidfVectorizer # import library tfidf dari sklearn untuk menghitung tf-idf dari data
from sklearn.metrics.pairwise import cosine_similarity # import library cosin similarity dari sklearn untuk menghitung cosine similaroty

pytrend = TrendReq() #inisialisasi obyek google trend api

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__))) # mendapatkan base direcrtory dari project ini
experience_dir = os.path.abspath(os.path.join(base_dir, "datasets/Experience.xlsx")) # join bash dir dengan dataset dir file
catalog_train = os.path.abspath(os.path.join(base_dir, "datasets/TrainingCatalog.xlsx")) # join bash dir dengan dataset dir file

experience = pd.read_excel(experience_dir) # membuka file excel experience.xlsx
experience = np.array(experience).flatten() # menjadikan array 1d
event_name = [] # inisialisasi list kosong
for i in experience: # perulangan dari data experience
    event_name.append(i.replace("\xa0", "")) # menghilangkan karakter \xa0 dari data
event_name = np.unique(event_name) # menghapus duplikasi data

catalog = pd.read_excel(catalog_train) # membuka file excel training catalog
catalog = np.array(catalog).flatten().tolist() # menjadikan ke array kemudian dijadikan array 1 dimensi
catalog = np.unique(catalog) # menghapus duplikasi data


def Cosim(corpus, query): # function cosim dengan parameter corpus dan query
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)) # inisialisasi obyek tfidf dengan parameter stopword english dan ngram 1 dan 2
    corpus_tfidf = vectorizer.fit_transform(corpus) # melakukan pembobotan kata korpus
    query_tfidf = vectorizer.transform([query]) # melakukan pembobotan query dengan data tf-idf dari corpus
    cosineSimilarities = cosine_similarity(query_tfidf, corpus_tfidf).flatten() # melakukan perhitungan cosine similarity kemudian dijadikan array 1 dimensi
    cosim_sort = np.sort(cosineSimilarities)[::-1] # melakukan pengurutan secara descending dari hasil cosine similarity

    concat = []
    for i in cosim_sort: # melakukan perulangan setiap nilai dari cosime yang sudah di sorting
        if i <= 0.5: # melakukan seleksi kondisi ketika nilai cosim nya kurang dari 0,5 maka 
            break # berhenti
        index_ke = np.where(cosineSimilarities == i) # melakukan pencarian index dari nilai cosime yang sudah di sort pada nilai cosine similarity yang belum di sort untuk didapatkan indexnya
        concat.append([corpus[index_ke[0][0]], i]) # melakukan pencarian corpus pada index yang sudah ditentukan kemudian dilakukan penggabungan pada setiap perulangan

    pd.set_option("display.max_colwidth", None) # melakukan perintah agar data bisa ditampilkan semua tidak (...)
    adf = pd.DataFrame(data=concat, columns=["corpus", "cosim value"]) # mengubah array menjadi dataframe dengan nama kolom corpus dan cosime value
    return adf


def train(query, topic):
    corpus = [event_name, catalog] # menjadikan event name dan katalog dalam 1 array, event_name index 0, catalog index 1

    count = []
    mean = []
    cosim_data = []
    for i in corpus: # melakukan perulangan pada corpus => event_name, catalog
        cosim = Cosim(i, query) # melakukan perhitungan cosim
        count.append(len(cosim)) # menggabung nilai dari panjang cosim
        mean.append(cosim["cosim value"].mean()) # menggabung nilai dari mean cosim
        cosim_data.append(cosim)

    pytrend.build_payload(kw_list=[topic]) # melakukan pencarian nilai dari query ke google trend api
    df = pytrend.interest_by_region() # melakukan pencarian by region
    jml_trend = np.array(df.loc["Indonesia"])[0] / 100 # mengambil nilai dari negara indonesia kemudian dibagi dengan 100
    mean.append(jml_trend) # menambahkan nilai dari jml_trend ke dalam variabel mean
    mean = np.nan_to_num(mean) # convert NaN value to 0
    return np.sum(mean), mean, cosim_data # mengembalikan jumlah dari rata-rata
