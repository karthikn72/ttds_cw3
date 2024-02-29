import pickle
import re
import sqlite3
from nltk import PorterStemmer
import pandas as pd
import numpy as np


class Indexer:
    
    def __init__(self) -> None:
        self.stemmer = PorterStemmer()
        self.stopwords = set()
        index_data = {}
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
    

    def indexing(self, database, offset):
        self.index_data = {}
        doc_no = offset
        
        for row in database.itertuples():
            doc_no += 1
            #row is in a df object. concat the title and article as a string
            title = str(row.title) if row.title is not None else ""
            article = str(row.article) if row.article is not None else ""
            text = title+' '+article
            text = self.preprocessing(text)
            for position,word in enumerate(text.split(), start=1):
                if word not in self.index_data:
                    self.index_data[word] = {}
                if doc_no not in self.index_data[word]:
                    self.index_data[word][doc_no] = []   
                self.index_data[word][doc_no].append(position)
        return "Indexing complete"
    
    def indexing_aao(self, database, offset):
        doc_no = offset
        for row in database:
            doc_no += 1
            text = row["title"]+' '+row["article"]
            text = self.preprocessing(text)
            for position,word in enumerate(text.split(), start=1):
                if word not in self.index_data:
                    self.index_data[word] = {}
                if doc_no not in self.index_data[word]:
                    self.index_data[word][doc_no] = []   
                self.index_data[word][doc_no].append(position)
        return "Indexing complete"
    

    def get_index(self):
        return self.index_data
                



    
    
    def output_pickle(self, filepath):
        sorted_postings = dict(sorted(self.index_data.items()))
        with open(filepath, 'wb') as outFile:
            try:
                pickle.dump(sorted_postings, outFile, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                print(e)
            else:
                print("Indexing complete")
                
    def output_txt(self, filepath, index_data):
        sorted_postings = dict(sorted(index_data.items()))
        with open(filepath, 'w') as outFile:
            for word in sorted_postings.keys():
                outFile.write(f'{word}:{index_data[word]["df"]}\n')
                for doc in index_data[word]["indexes"]:
                    outFile.write(f' {doc}:{index_data[word]["indexes"][doc]["positions"]}\n')
            print("Indexing complete")
        outFile.close()






