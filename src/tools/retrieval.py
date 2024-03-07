import heapq
import numpy as np

from tokenizer import QueryTokenizer


DEFAULT_INDEX_FILE = 'tools\index.txt'

class TFIDFScoring:
    def __init__(self, index_filename=DEFAULT_INDEX_FILE):
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
                    word_freq = len(p[1].split(','))
                    self.index[last_term][docno] = word_freq
                    docset.add(docno)
        self.N = len(docset)

        self.weights = {}

    def score(self, query_terms, k=150):
        score = {}
        for term in query_terms:
            for doc in self.index[term]:
                if doc not in score:
                    score[doc] = 0
                tf = (1 + np.log10(self.index[term][doc])) # l
                idf = np.log10(self.N/len(self.index[term])) # t
                score[doc] += tf * idf
        
        # (TODO) add cosine normalisation (lnc.ltc)
        return list(map(lambda doc: (doc, format(score[doc], '.4f')), heapq.nlargest(k, score, key=score.get)))

if __name__ == '__main__':
    query = 'call denver direct'

    qtokenizer = QueryTokenizer()
    query_terms = qtokenizer.tokenize(query)

    r = TFIDFScoring()
    print(r.score(query_terms))
