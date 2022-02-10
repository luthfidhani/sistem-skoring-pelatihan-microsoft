import numpy as np 
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer 
from sklearn.metrics.pairwise import cosine_similarity 
from pytrends.request import TrendReq 

pytrend = TrendReq() 

base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)))
experience_dir = os.path.abspath(os.path.join(base_dir, 'datasets/Experience.xlsx'))
catalog_train = os.path.abspath(os.path.join(base_dir, 'datasets/TrainingCatalog.xlsx'))

experience = pd.read_excel(experience_dir) 
experience = np.array(experience)[:,2] 
event_name = [] 
for i in experience: 
    event_name.append(i.replace("\xa0", "")) 
event_name = np.unique(event_name) 

catalog = pd.read_excel(catalog_train) 
catalog = np.array(catalog).flatten().tolist() 
catalog = np.unique(catalog) 

def Cosim(corpus, query): 
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2)) 
    corpus_tfidf = vectorizer.fit_transform(corpus) 
    query_tfidf = vectorizer.transform([query]) 
    cosineSimilarities = cosine_similarity(query_tfidf, corpus_tfidf).flatten() 
    cosim_sort = np.sort(cosineSimilarities)[::-1] 

    concat = []
    for i in cosim_sort: 
        if i <= 0.5: 
            break 
        index_ke = np.where(cosineSimilarities == i)   
        concat.append([corpus[index_ke[0][0]], i]) 
    
    pd.set_option('display.max_colwidth', None) 
    adf = pd.DataFrame(data=concat, columns=['corpus', 'cosim value']) 

    return adf 

def train(query, topic):
    corpus = [event_name, catalog]

    count = []
    mean = []
    for i in corpus: 
        cosim = Cosim(i, query) 
        count.append(len(cosim)) 
        mean.append(cosim['cosim value'].mean()) 

    pytrend.build_payload(kw_list=[topic]) 
    df = pytrend.interest_by_region() 
    jml_trend = np.array(df.loc["Indonesia"])[0]/100 
    mean.append(jml_trend) 
    return np.sum(mean)