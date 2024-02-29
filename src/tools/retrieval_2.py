from collections import defaultdict
import heapq
import pickle
import sys
import os

import numpy as np
# sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from .tokenizer import Tokenizer, QueryTokenizer

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

DEFAULT_INDEX_FILE = 'index_tfidf.pkl'

class Retrieval:
    def __init__(self, index_filename=DEFAULT_INDEX_FILE):
        with open(index_filename, 'rb') as f:
            self.index = pickle.load(f)
        # Construct a set of all documents in the index
        docset = set()
        for word_info in self.index.values():
            docset.update(word_info['indexes'].keys())
        self.N = len(docset)  # Total number of documents
        # Placeholder for document weights, for normalization
        
        
    def ranked_retrieval(self, query_terms, k=20): #needs to be redone, this is based on the tfidf calculator that used to be there, not actually the right way to do it
        score = self.__bow_docs_retrieval(query_terms)

        return list(map(lambda doc: (doc, format(score[doc], '.4f')), heapq.nlargest(k, score, key=score.get)))
    
    def __bow_docs_retrieval(self, query_terms):
        scores = defaultdict(lambda: float)
        for term in query_terms:
            if term in self.index:
                for doc in self.index[term]:
                    if doc not in scores:
                        scores[doc] = 0
                    scores[doc] += self.index[term]['indexes'][doc]['tfidf']
        # (TODO) add cosine normalisation (lnc.ltc)
        return scores
    
    def bool_search(self, query_terms1, query_terms2=[], operator=None):

        docs1 = list(self.__bow_docs_retrieval(query_terms1).keys()) if query_terms1 and query_terms1[0]!=" " else self.__phrase_search(query_terms1[1:])
        docs2 = list(self.__bow_docs_retrieval(query_terms2).keys()) if query_terms2 and query_terms2[0]!=" " else self.__phrase_search(query_terms2[1:])

        if not operator:
            return docs1

        if operator == 'AND':
            return docs1 & docs2
        
        return docs1 | docs2
    
    def __phrase_search(self, terms):
        if len(terms)==0:
            return set([])
        
        if len(terms)==1:
            return set(self.index[terms[0]]['indexes'].keys())

        for i in range(0, len(terms)-1):
            term1 = terms[i]
            term2 = terms[i+1]

            if (term1 not in self.index)|(term2 not in self.index):
                return set([])
            
            if i==0:
                docs1 = set(self.index[term1]['indexes'].keys())
                term1_dict = {key: np.asarray(inner_dict['positions']) for key, inner_dict in self.index[term1]['indexes'].items()} 
            else:
                docs1 = set(output_dict.keys())
                term1_dict = output_dict
            docs2 = set(self.index[term2]['indexes'].keys())
            term2_dict = {key: np.asarray(inner_dict['positions']) for key, inner_dict in self.index[term2]['indexes'].items()}
            shared_docs = docs1 & docs2

            output_dict = self.__check_adjacent_words(shared_docs, term1_dict, term2_dict)

            if len(output_dict)==0:
                return set([])
        
        return set(output_dict.keys())
    
    def __check_adjacent_words(self, shared_docs, former_pos_dict, later_pos_dict):
        proximity = 1
        output_dict = defaultdict(list)
        for doc in shared_docs:
            term1_positions = former_pos_dict[doc] + proximity
            term2_positions = later_pos_dict[doc]

            # print(doc, term1_positions, term2_positions)

            phrase_pos = np.intersect1d(term1_positions, term2_positions)

            if len(phrase_pos) > 0:
                output_dict[doc] = phrase_pos
            
        return dict(output_dict)
    
if __name__ == '__main__':
    # query = 'call denver direct'

    query = '"people told matter"'
    qtokenizer = QueryTokenizer()
    query_terms1, query_terms2, operator = qtokenizer.tokenize(query)

    r = Retrieval()
    print(r.bool_search(query_terms1, query_terms2, operator))
