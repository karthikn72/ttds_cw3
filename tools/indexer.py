import pickle
import re
from nltk import PorterStemmer
import pandas as pd
import numpy as np


class Indexer:
    def __init__(self) -> None:
        self.stemmer = PorterStemmer()
        self.stopwords = set()
        pass

    def set_up_stopwords(self, filepath):
        with open(filepath) as stopFile:
            self.stopwords = set(stopFile.read().splitlines())


    def preprocessing(self, line, stopping=True, stemming=True):
        line = line.replace('\'', ' ')
        line = line.replace('-', ' ')
        pattern = re.compile('[a-zA-Z0-9 \n]+')
        result = ''.join(pattern.findall(re.sub('\n', ' ', line.lower())))
        if stopping and stemming:
            filtered_lines = [self.stemmer.stem(word) for word in result.split() if word not in self.stopwords]
        elif stopping:
            filtered_lines = [word for word in result.split() if word not in self.stopwords]
        elif stemming:
            filtered_lines = [self.stemmer.stem(word) for word in result.split()]
        else:
            filtered_lines = [word for word in result.split()]
        return ' '.join(filtered_lines).rstrip()
    

    def indexing(self, filepath):
        news = pd.read_csv(filepath,quotechar='"')
        
        news = news.dropna(subset=['article'])
        N = len(news)
        index_data = {}  
    # {
    #     word: {
    #         'df': int, occurences in the corpus
    #         'indexes': {
    #             doc_no: {
    #                 'positions': [int],
    #                 'tf':int, occurences in the document
    #                 'tfidf': float
    #             }
    #         }
    #     }
    # }
        for doc_no, doc in news.iterrows():
            text = doc["article"]
            text = self.preprocessing(text)
            seen = set()
            for position,word in enumerate(text.split(), start=1):
                if word not in index_data:
                    index_data[word] = {'df': 0, 'indexes': {}}
                if word not in seen:
                    index_data[word]['df'] += 1
                    seen.add(word)
                if doc_no not in index_data[word]['indexes']:
                    index_data[word]['indexes'][doc_no] = {}
                    index_data[word]['indexes'][doc_no]['positions'] = []
                    index_data[word]['indexes'][doc_no]['tf'] = 0   
                index_data[word]['indexes'][doc_no]['positions'].append(position)
                index_data[word]['indexes'][doc_no]['tf'] += 1
        self.tfidf(index_data, N)
        self.output_pickle('index_tfidf.pkl', index_data)
        

    def tfidf(self, index_data, N):
        for word in index_data:
            for doc in index_data[word]['indexes']:
                tf = 1 + np.log10(index_data[word]['indexes'][doc]['tf'])
                idf = np.log10(N/index_data[word]['df'])
                index_data[word]['indexes'][doc]['tfidf'] = tf * idf
    
    
    def output_pickle(self, filepath, index_data):
        sorted_postings = dict(sorted(index_data.items()))
        with open(filepath, 'wb') as outFile:
            try:
                pickle.dump(sorted_postings, outFile, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                print(e)
            else:
                print("Indexing complete")
