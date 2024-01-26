import heapq
import numpy as np

import sys
sys.path.append('/Users/nivedark/Desktop/ttds_cw3')
from tools.tokenizer import Tokenizer


DEFAULT_INDEX_FILE = '../index_generation/index.txt'

class TFIDFScoring:
    def __init__(self, index_filename=DEFAULT_INDEX_FILE):
        self.tokenizer = Tokenizer()

        docset = set()
        with open(index_filename, 'r') as f:
            lines = f.read().splitlines()

            last_term = ""
            self.index = {}
            for line in lines:
                p = line.strip().split(' ')
                if len(p) == 1:
                    word, _ = line.split(':')
                    self.index[word] = {}
                    last_term = word
                else:
                    docno = int(p[0][:-1])
                    word_freq =  len(p[1].split(','))
                    self.index[last_term][docno] = word_freq
                    docset.add(docno)
        self.N = len(docset)

        self.weights = {}

    def score(self, query, k=150):
        query_terms = self.tokenizer.tokenize(query)

        score = {}
        for term in query_terms:
            for doc in self.index[term]:
                if doc not in score:
                    score[doc] = 0
                score[doc] += (1 + np.log10(self.index[term][doc])) * np.log10(self.N/len(self.index[term]))

        return list(map(lambda doc: (doc, format(score[doc], '.4f')), heapq.nlargest(k, score, key=score.get)))

if __name__ == '__main__':
    r = TFIDFScoring()
    print(r.score('call denver direct'))
