import heapq
import numpy as np
import pickle
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from tools.tokenizer import Tokenizer

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

DEFAULT_INDEX_FILE = '../index_generation/index.pkl'

class Retrieval:
    def __init__(self, index_filename=DEFAULT_INDEX_FILE):
        self.tokenizer = Tokenizer()
        with open(index_filename, 'rb') as f:
            self.data = pickle.load(f)
        # Construct a set of all documents in the index
        docset = set()
        for word_info in self.data.values():
            docset.update(word_info['indexes'].keys())
        self.N = len(docset)  # Total number of documents
        # Placeholder for document weights, for normalization
        
        
    def get_query_docs(self, query, k=20):
        query_terms = self.tokenizer.tokenize(query)

        score = {}
        for term in query_terms:
            for doc in self.data[term]['indexes']:
                if doc not in score:
                    score[doc] = 0
                
                score[doc] += self.data[term]['indexes'][doc]['tfidf']
        
        # (TODO) add cosine normalisation (lnc.ltc)
        return list(map(lambda doc: (doc, format(score[doc], '.4f')), heapq.nlargest(k, score, key=score.get)))
    
    def get_index(self, word): #path is now a .pkl file
        output ={}
        for doc in self.data[word]['indexes']:
            output[doc] = self.data[word]['indexes'][doc]['positions']
        
        return output

        
        

if __name__ == '__main__':
    r = Retrieval('/Users/dagafed/Documents/GitHub/ttds_cw3/tools/index_tfidf.pkl')
    print(r.get_query_docs('call denver direct'))
    print(r.get_index("0"))
