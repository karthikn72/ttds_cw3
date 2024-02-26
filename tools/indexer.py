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
    # new implementation
    # {
    #     word: {
    #             doc:[int]
    #             }
    #     }
    # }   
    #      
        # news = pd.read_csv(filepath,quotechar='"')
        
        # news = news.dropna(subset=['article'])
        # N = len(news)  
        # for doc_no, doc in news.iterrows():
        #     text = doc["article"]
        #     text = self.preprocessing(text)
        #     seen = set()
        #     for position,word in enumerate(text.split(), start=1):
        #         if word not in index_data:
        #             index_data[word] = {'df': 0, 'indexes': {}}
        #         if word not in seen:
        #             index_data[word]['df'] += 1
        #             seen.add(word)
        #         if doc_no not in index_data[word]['indexes']:
        #             index_data[word]['indexes'][doc_no] = {}
        #             index_data[word]['indexes'][doc_no]['positions'] = []
        #             index_data[word]['indexes'][doc_no]['tf'] = 0   
        #         index_data[word]['indexes'][doc_no]['positions'].append(position)
        #         index_data[word]['indexes'][doc_no]['tf'] += 1

        # # if format == 'txt':
        #     self.output_txt('index_tfidf.txt', index_data)
        # if format == 'pkl':
        #     self.output_pickle('index_tfidf.pkl', index_data)
        # if format == 'dbs':
        #     self.output_database(index_data)

        


    
    
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

    # def output_database(self, index_data):
    #     #create word table, document table and word in document table
    #     #using SQLite3 for now
    #     sorted_postings = dict(sorted(index_data.items()))
    #     conn = sqlite3.connect('words.db')
    #     cur = conn.cursor()
    #     cur.execute('''CREATE TABLE IF NOT EXISTS Words
    #            (word_id INTEGER PRIMARY KEY, word TEXT UNIQUE, df INTEGER)''')
    #     cur.execute('''CREATE TABLE IF NOT EXISTS Documents
    #                 (doc_id INTEGER PRIMARY KEY, doc_no INTEGER UNIQUE )''')
    #     cur.execute('''CREATE TABLE IF NOT EXISTS WordInDoc
    #                 (word_id INTEGER, doc_id INTEGER, tf INTEGER, tfidf REAL, positions TEXT)''')
    #     conn.commit()
    #     for word in         sorted_postings.keys() :
    #         cur.execute("INSERT OR IGNORE INTO Words (word, df) VALUES (?,?)",(word, sorted_postings[word]['df']))
    #         for doc in index_data[word]['indexes']:
    #             cur.execute("INSERT OR IGNORE INTO Documents (doc_no) VALUES (?)",(doc,))
    #             cur.execute("SELECT word_id FROM Words WHERE word = ?",(word,))
    #             word_id = cur.fetchone()[0]
    #             cur.execute("SELECT doc_id FROM Documents WHERE doc_no = ?",(doc,))
    #             doc_id = cur.fetchone()[0]
    #             cur.execute("INSERT INTO WordInDoc (word_id, doc_id, tf, tfidf, positions) VALUES (?,?,?,?,?)",(word_id, doc_id, index_data[word]['indexes'][doc]['tf'], index_data[word]['indexes'][doc]['tfidf'], str(index_data[word]['indexes'][doc]['positions'])))
        
    #     #save the database
    #     conn.commit()
    #     conn.close()

    #     print("Indexing complete")








