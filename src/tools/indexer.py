import pickle
import re
from nltk import PorterStemmer
import pandas as pd
import numpy as np
import timer
from tokenizer import Tokenizer
from tqdm import tqdm

class Indexer:
    
    def __init__(self, case_fold=True, stop=True,  stem=True ):
        self.tokenizer = Tokenizer( case_fold=case_fold, stop=stop,  stem=stem)
        
    def preprocessing(self, line):
        return self.tokenizer.tokenize(line)
    def set_up_stopwords(self, filepath):
        pass
    
    def indexing(self, article_df):
        self.index_data = {}
        n = len(article_df)
        for row in tqdm(article_df.itertuples(), total=n):
            doc_no = row.article_id
            #row is in a df object. concat the title and article as a string
            title = str(row.title) if row.title is not None else ""
            article = str(row.article) if row.article is not None else ""
            text = title+' '+article
            text = self.preprocessing(text)
            for position,word in enumerate(text, start=1):
                if word not in self.index_data:
                    self.index_data[word] = {}
                if doc_no not in self.index_data[word]:
                    self.index_data[word][doc_no] = []   
                self.index_data[word][doc_no].append(position)
        
        # Turn self.index_data into a list of tuples
        index_list = []
        for word, doc_data in self.index_data.items():
            for doc, positions in doc_data.items():
                index_list.append((word, doc, positions))
        
        #turn the list of tuples into a dataframe
        self.index_df = pd.DataFrame(index_list, columns=['word', 'article_id', 'positions'])
        return "Indexing complete"

    def get_index(self):
        return self.index_df
    
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

if __name__ == "__main__":
    idxer = Indexer()
    idxer.set_up_stopwords("resources/ttds_2023_english_stop_words.txt")
    db = pd.read_csv("first1000.csv")
    
    #get me just the values in index for the most numerous word
    #time this operation
    atimer = timer.Timer("Indexed 1 in {:.4f}s")
    atimer.start()
    idxer.indexing(0, db)
    df1 = idxer.get_index()
    print(df1)
    atimer.stop()
    btimer = timer.Timer("Indexed 2 in {:.4f}s")
    btimer.start()
    idxer.indexing2(0, db)
    df2 = idxer.get_index()
    btimer.stop()
    print(df2)

    







