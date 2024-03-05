from collections import defaultdict
import heapq
import pickle
import sys
import os

import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.pardir)))
from tokenizer import Tokenizer, QueryTokenizer

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
        docset = set()
        for word_info in self.index.values():
            docset.update(word_info['indexes'].keys())
        self.N = len(docset)  # Total number of documents

    def free_form_retrieval(self, query_terms):
        doc_scores = defaultdict(lambda: float)
        for term in query_terms:
            if type(term) == str and term in self.index:
                for doc in self.index[term]['indexes']:
                    if doc not in doc_scores:
                        doc_scores[doc] = 0
                    doc_scores[doc] += self.index[term]['indexes'][doc]['tfidf']
            elif type(term)==list:
                phrase_docs = self.__phrase_search(term)
                for w in term:
                    for doc in phrase_docs:
                        if doc not in doc_scores:
                            doc_scores[doc] = 0
                        doc_scores[doc] += self.index[w]['indexes'][doc]['tfidf']

        return doc_scores
    
    def bool_retrieval(self, query_terms1, query_terms2=[], operator=None):
        docs1 = self.free_form_retrieval(query_terms1)
        docs2 = self.free_form_retrieval(query_terms2)

        if not operator:
            return docs1

        if operator == 'AND':
            docs = docs1.keys() & docs2.keys()
        else:
            docs = docs1.keys() | docs2.keys()
        
        docs_scores = defaultdict(lambda: float)
        for doc in docs:
            if doc not in docs_scores:
                docs_scores[doc] = 0
            docs_scores[doc] = docs1[doc]+docs2[doc]
        
        return docs_scores
    
    def proximity_retrieval(self, word1, word2, proximity):
        doc_scores = defaultdict(lambda: float)
        
        if (word1 not in self.index) or (word2 not in self.index):
            return doc_scores
        
        word1_doc_pos = {key: np.asarray(inner_dict['positions']) for key, inner_dict in self.index[word1]['indexes'].items()} 
        word2_doc_pos = {key: np.asarray(inner_dict['positions']) for key, inner_dict in self.index[word2]['indexes'].items()}

        common_docs = word1_doc_pos.keys() & word2_doc_pos.keys()

        docs = set([])
        for p in range(1, proximity+1):
            docs = docs | self.__check_adjacent_words(common_docs, word1_doc_pos, word2_doc_pos, p).keys()

        for w in [word1, word2]:
            for doc in docs:
                if doc not in doc_scores:
                    doc_scores[doc] = 0
                doc_scores[doc] += self.index[w]['indexes'][doc]['tfidf']

        return doc_scores
    
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
    
    def __check_adjacent_words(self, shared_docs, former_pos_dict, later_pos_dict, proximity=1):
        output_dict = defaultdict(list)
        for doc in shared_docs:
            term1_positions = former_pos_dict[doc] + proximity
            term2_positions = later_pos_dict[doc]

            phrase_pos = np.intersect1d(term1_positions, term2_positions)

            if len(phrase_pos) > 0:
                output_dict[doc] = phrase_pos
            
        return dict(output_dict)
    
if __name__ == '__main__':
    # query = 'call denver direct'

    query = '"people told matter" AND call denver direct'
    qtokenizer = QueryTokenizer()
    query1, query2, o = qtokenizer.tokenize_bool(query)

    r = Retrieval()
    print(r.proximity_retrieval('middl', 'east', 3))
