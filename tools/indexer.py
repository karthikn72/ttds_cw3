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

        postings = {}
        doc_count = {}

        for index, doc in news.iterrows():
            # write to database

            idx = 1
            text = doc["article"]
            
            text = self.preprocessing(text)

            positions_within_doc = {}
            for word in text.split():
                if word not in positions_within_doc:
                    positions_within_doc[word] = []
                positions_within_doc[word].append(idx)
                idx += 1
            
            for word in positions_within_doc.keys():
                all_positions = ''
                for position in positions_within_doc[word]:
                    all_positions += f'{position},'
                all_positions = all_positions[:-1]
                if word not in postings:
                    postings[word] = []
                postings[word].append(f'{index}: {all_positions}\n')

                if word not in doc_count:
                    doc_count[word] = 0
                doc_count[word] += 1

        self.output('index.txt', postings, doc_count)


    def output(self, filepath, postings, doc_count):

        with open('index.txt', 'w') as outFile:
            sorted_postings = dict(sorted(postings.items()))
            for word in sorted_postings.keys():
                outFile.write(f'{word}:{doc_count[word]}\n')
                for positions in sorted_postings[word]:
                    outFile.write(' ' * 3 + positions)

        outFile.close()

if __name__ == "__main__":
    idxer = Indexer()
    idxer.indexing()
