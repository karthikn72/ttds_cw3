import heapq
import numpy as np
import pickle
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from tools.tokenizer import Tokenizer



DEFAULT_INDEX_FILE = '../index_generation/index.pkl'

class TFIDFScoring:
    def __init__(self, index_filename=DEFAULT_INDEX_FILE):
        self.tokenizer = Tokenizer()

        
        # with open(index_filename, 'r') as f:
        #     lines = f.read().splitlines()

        #     last_term = ""
        #     self.index = {}
        #     for line in lines:
        #         p = line.strip().split(' ')
        #         if len(p) == 1:
        #             word, _ = line.split(':')
        #             self.index[word] = {}
        #             last_term = word
        #         else:
        #             docno = int(p[0][:-1])
        #             word_freq =  len(p[1].split(','))
        #             self.index[last_term][docno] = word_freq
        #             docset.add(docno)
        #open from pickle with format {word: {'doc_count': int, 'indexes': {doc_no: {'positions': [int]}}}}
        with open(index_filename, 'rb') as f:
            data = pickle.load(f)
        
        
        # Construct a set of all documents in the index
        docset = set()
        for word_info in data.values():
            docset.update(word_info['indexes'].keys())

        self.N = len(docset)  # Total number of documents

        # Placeholder for document weights, for normalization
        self.index = {}
        for word in data:
            self.index[word] = {}
            for doc in docset:
                if doc in data[word]['indexes']:
                    self.index[word][doc] = len(data[word]['indexes'][doc]['positions'])
                else:
                    self.index[word][doc] = 0
        
        
    def score(self, query, k=150):
        query_terms = self.tokenizer.tokenize(query)

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
    def word_score (self, word):
        score = {}
        if word not in self.index:
            return score
        for doc in self.index[word]:
            if doc not in score:
                score[doc] = 0
            tf = (1 + np.log10(self.index[word][doc]))
            idf = np.log10(self.N/len(self.index[word]))
            score[doc] += tf * idf
        return score
    def update_index(self, index_filename = DEFAULT_INDEX_FILE):
        with open(index_filename, 'rb') as f:
            data = pickle.load(f)
        for word in data:
            tfidf_scores = self.word_score(word)
            for doc in data[word]['indexes']:
                if doc in tfidf_scores:
                    data[word]['indexes'][doc]['tfidf'] = tfidf_scores[doc]
                else:
                    pass
        with open(index_filename, 'wb') as f:
            pickle.dump(data, f)
        return data

            

                
        #goal is to add tfidf score for each word into dict,
        #assume that the index is structured as {word: {'doc_count': int, 'indexes': {doc_no: {'positions': [int], 'tfidf': float}}}}
        
        

if __name__ == '__main__':
    r = TFIDFScoring()
    r.update_index()

    print(r.score('call denver direct'))
