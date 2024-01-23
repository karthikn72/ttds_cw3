import re
from nltk import PorterStemmer
import numpy as np
import timeit
import pandas as pd

# ------------------ Read From Dataset -----------------

# IMPORTANT: If you were to run this code, make sure to download the dataset and change the path to it. 


news = pd.read_csv('all-the-news-2-1\\all-the-news-2-1.csv', nrows=10)
news = news.dropna(subset=['article'])

# ------------------ Pre-processing --------------------
stemmer = PorterStemmer()
stop_words = set()

stopping = False
stemming = True

with open('ttds_2023_english_stop_words.txt') as stopFile:
    stop_words = set(stopFile.read().splitlines())

def preprocessing(line):
    line = line.replace('\'', ' ')
    line = line.replace('-', ' ')
    pattern = re.compile('[a-zA-Z0-9 \n]+')
    result = ''.join(pattern.findall(re.sub('\n', ' ', line.lower())))
    if stopping and stemming:
        filtered_lines = [stemmer.stem(word) for word in result.split() if word not in stop_words]
    elif stopping:
        filtered_lines = [word for word in result.split() if word not in stop_words]
    elif stemming:
        filtered_lines = [stemmer.stem(word) for word in result.split()]
    else:
        filtered_lines = [word for word in result.split()]
    return ' '.join(filtered_lines).rstrip()


# ------------------ Indexing --------------------
postings = {}
doc_count = {}

for index, doc in news.iterrows():
    # write to database

    idx = 1
    text = doc["article"]
    
    text = preprocessing(text)

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

with open('index.txt', 'w') as outFile:
    sorted_postings = dict(sorted(postings.items()))
    for word in sorted_postings.keys():
        outFile.write(f'{word}:{doc_count[word]}\n')
        for positions in sorted_postings[word]:
            outFile.write(' ' * 3 + positions)

outFile.close()