import pickle
import re
from nltk import PorterStemmer
import pandas as pd
import numpy as np
import timer

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
    

    def indexing(self, offset, database):
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
        
        # Turn self.index_data into a list of tuples
        index_list = []
        for word, doc_data in self.index_data.items():
            for doc, positions in doc_data.items():
                index_list.append((word, doc, positions))
        
        #turn the list of tuples into a dataframe
        self.index_df = pd.DataFrame(index_list, columns=['word', 'article_id', 'positions'])
        # self.index_df = self.index_df.sort_values(by=['word', 'article_id']).reset_index(drop=True)
        return "Indexing complete"
    
    def indexing2(self, offset, database):
        self.index_data = {}
        doc_no = offset
        index_list = []
        for row in database.itertuples():
            doc_no += 1
            #row is in a df object. concat the title and article as a string
            title = str(row.title) if row.title is not None else ""
            article = str(row.article) if row.article is not None else ""
            text = title+' '+article
            text = self.preprocessing(text)
            for position,word in enumerate(text.split(), start=1):
                index_list.append((word, doc_no, position))
        
        self.index_df = pd.DataFrame(index_list, columns=['word', 'doc', 'postings'])
        self.index_df = self.index_df.groupby(['word','doc'])['postings'].apply(list).reset_index()

        return "Indexing complete"
        

    #     return "Indexing complete"
    # def indexing2(self, offset, database):

    #     self.index_df = pd.DataFrame(columns=['word', 'doc', 'postings'])
    #     doc_no = offset
    #     for row in database.itertuples():
    #         doc_no += 1
    #         #row is in a df object. concat the title and article as a string
    #         title = str(row.title) if row.title is not None else ""
    #         article = str(row.article) if row.article is not None else ""
    #         text = title+' '+article
    #         text = self.preprocessing(text)
    #         for position,word in enumerate(text.split(), start=1):
    #             #add a row to the index dataframe
    #             self.index_df = self.index_df.append({'word':word, 'doc':doc_no, 'postings':position}, ignore_index=True)
    #     self.index_df = self.index_df.groupby(['word', 'doc'])['postings'].apply(list).reset_index(name='new')
        
                
    #     return "indexing complete"

    
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
        index_list = []
        for word, doc_data in self.index_data.items():
            for doc, positions in doc_data.items():
                index_list.append((word, doc, positions))
        self.index_df = pd.DataFrame(index_list, columns=['word', 'doc', 'postings'])
        self.index_df = self.index_df.sort_values(by=['word', 'doc'])
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

    







