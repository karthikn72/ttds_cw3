import pickle
import re
from nltk import PorterStemmer
import pandas as pd



class Indexer:
    def __init__(self) -> None:
        self.stemmer = PorterStemmer()
        self.stopwords = set()
        pass

    def set_up_stopwords(self, filepath):
        with open(filepath) as stopFile:
            self.stop_words = set(stopFile.read().splitlines())


    def preprocessing(self, filepath, stopping=True, stemming=True):
        line = line.replace('\'', ' ')
        line = line.replace('-', ' ')
        pattern = re.compile('[a-zA-Z0-9 \n]+')
        result = ''.join(pattern.findall(re.sub('\n', ' ', line.lower())))
        if stopping and stemming:
            filtered_lines = [self.stemmer.stem(word) for word in result.split() if word not in self.stop_words]
        elif stopping:
            filtered_lines = [word for word in result.split() if word not in self.stop_words]
        elif stemming:
            filtered_lines = [self.stemmer.stem(word) for word in result.split()]
        else:
            filtered_lines = [word for word in result.split()]
        return ' '.join(filtered_lines).rstrip()
    

    def indexing(self, filepath):
        news = pd.read_csv(filepath)
        news = news.dropna(subset=['article'])

        index_data = {}  # {word: {'doc_count': int, 'indexes': {doc_no: {'positions': [int]}}}}
        for doc_no, doc in news.iterrows():
            text = doc["article"]
            text = self.preprocessing(text)
            seen = set()
            for position,word in enumerate(text.split(), start=1):
                if word not in index_data:
                    index_data[word] = {'doc_count': 0, 'indexes': {}}
                if word not in seen:
                    index_data[word]['doc_count'] += 1
                    seen.add(word)
                if doc_no not in index_data[word]['indexes']:
                    index_data[word]['indexes'][doc_no]['positions'] = []   
                index_data[word]['indexes'][doc_no]['positions'].append(position)
        self.output_pickle('index.pkl', index_data)


    def output_pickle(self, filepath, index_data):
        sorted_postings = dict(sorted(index_data.items()))
        with open(filepath, 'wb') as outFile:
            pickle.dump(sorted_postings, outFile)
        outFile.close()
    


if __name__ == "__main__":
    idxer = Indexer()
    idxer.indexing()
