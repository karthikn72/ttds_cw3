import pickle
import re
from nltk import PorterStemmer
import pandas as pd
import numpy as np


class Indexer:
    
    def __init__(self) -> None:
        self.stemmer = PorterStemmer()
        self.stopwords = set()
        self.index_data = {}
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
        #test data
        # documents = [
        #     (1, "In the midst of the chaos, a single midst midst voice emerged, clear and unwavering, cutting through the tumult like a beacon of hope."),
        #     (2, "Underneath the ancient oak, secrets of the past whispered on the wind, telling tales of forgotten lands and dreams that once were."),
        #     (3, "Amidst the shadows of the forgotten library, the scholar uncovered truths so profound that the fabric of reality seemed to tremble at their revelation."),
        #     (4, "The storm raged on, a tempest of fury and lightning, echoing the turmoil within the hearts of those who dared to challenge the sea."),
        #     (5, "In the heart of the bustling city, amidst the cacophony of sounds and the kaleidoscope of lights, a solitary figure stood still, a silent observer to the unfolding drama."),
        #     (6, "Beneath the serene surface of the lake, ancient creatures stirred, awakening from their slumber to the moon's gentle call."),
        #     (7, "The artist painted with strokes of passion and despair, each brushstroke a testament to the tumultuous journey of the soul."),
        #     (8, "Through the dense foliage of the untamed jungle, the explorer pressed on, driven by an insatiable curiosity and the lure of undiscovered wonders."),
        #     (9, "As the sun dipped below the horizon, casting the world in a golden glow, the weary travelers found solace in the beauty of the end of another day."),
        #     (10, "The melody of the night was woven from the whispers of the stars, the sighing of the wind, and the distant call of the nocturnal creatures, a symphony of the unseen."),
        # ]
        # for doc in documents:
        #     doc_no = doc[0]
        #     text = doc[1]
        ### OPTION 1 ###
        self.index_data = pd.DataFrame(columns=['word', 'doc', 'postings'])
        doc_no = offset
        for row in database.itertuples():
            doc_no += 1
            #row is in a df object. concat the title and article as a string
            title = str(row.title) if row.title is not None else ""
            article = str(row.article) if row.article is not None else ""
            text = title+' '+article
            text = self.preprocessing(text)
            #for each pair of word and doc_no, add a new row to the index_data df with an empty array postings value
            for position,word in enumerate(text.split(), start=1):
                if not ((self.index_data['word'] == word) & (self.index_data['doc'] == doc_no)).any():
                    self.index_data = pd.concat([self.index_data, pd.DataFrame({'word': [word], 'doc': [doc_no], 'postings': [[position]]})], ignore_index=True)
                else:
                    self.index_data.loc[(self.index_data['word'] == word) & (self.index_data['doc'] == doc_no), 'postings'].apply(lambda x: x.append(position))
        return self.index_data

        ### OPTION 2 ###
        self.index_data = pd.DataFrame(columns=['word', 'doc', 'postings'])
        doc_no = offset
        for row in database.itertuples():
            doc_no += 1
            #row is in a df object. concat the title and article as a string
            title = str(row.title) if row.title is not None else ""
            article = str(row.article) if row.article is not None else ""
            text = title+' '+article
            text = self.preprocessing(text)
            words = []
            for position, word in enumerate(text.split(), start=1):
                if word not in words:
                    words.append(word)  
                    self.index_data = pd.concat([self.index_data, pd.DataFrame({'word': [word], 'doc': [doc_no], 'postings': [[position]]})], ignore_index=True)
                else:
                    self.index_data.loc[(self.index_data['word'] == word) & (self.index_data['doc'] == doc_no), 'postings'].apply(lambda x: x.append(position))
        return self.index_data
        ### OPTION 3 ###
        #create a separate pd.dataframe for each word, then merge them all together
        doc_no = offset
        words = {}
        for row in database.itertuples():
            doc_no += 1
            #row is in a dataframe object. concat the title and article as a string
            title = str(row.title) if row.title is not None else ""
            article = str(row.article) if row.article is not None else ""
            text = title+' '+article
            text = self.preprocessing(text)
            doc_words = []
            for position,word in enumerate(text.split(), start=1):
                if word not in words:
                    words.append(word)
                    word_df = pd.DataFrame(columns=['word', 'doc', 'postings'])
                else:
                    word_df = words[word]
                if word not in doc_words:
                    doc_words.append(word)
                    word_df = pd.concat([word_df, pd.DataFrame({'word': [word], 'doc': [doc_no], 'postings': [[position]]})], ignore_index=True)
                else:
                    word_df.loc[(word_df['word'] == word) & (word_df['doc'] == doc_no), 'postings'].apply(lambda x: x.append(position)) 
                words[word] = word_df
        self.index_data = pd.concat(words.values(), ignore_index=True)
        return self.index_data
        



    

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
if __name__ == "__main__":
    indexer = Indexer()
    indexer.set_up_stopwords('resources/ttds_2023_english_stop_words.txt')
    df = indexer.indexing()
    print(df)






