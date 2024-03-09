from collections import defaultdict
import heapq
import pickle
import sys
import os
from .database import Database

import numpy as np
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

class Retrieval:
    def __init__(self):
        self.db = Database()
    
    def __flatten_query_terms(self, query_terms):
        flat_list = []
        for row in query_terms:
            if type(row)==list:
                flat_list.extend(row)
            else:
                flat_list.append(row)
        return flat_list

    def free_form_retrieval(self, query_terms):
        self.index = self.db.get_index_by_words(self.__flatten_query_terms(query_terms))
        
        doc_scores = defaultdict(lambda: float)
        for term in query_terms:
            if type(term) == str:
                term_index = self.index[self.index['word']==term]
                for doc in term_index['article_id']:
                    if doc not in doc_scores:
                        doc_scores[doc] = 0
                    doc_scores[doc] += term_index[term_index.article_id==doc]['tfidf'].values[0]
            elif type(term)==list:
                phrase_docs = self.__phrase_search(term)
                for w in term:
                    for doc in phrase_docs:
                        if doc not in doc_scores:
                            doc_scores[doc] = 0
                        
                        doc_scores[doc] += self.index[(self.index['word'] == w) & (self.index['article_id'] == doc)]['tfidf'].values[0]

        return doc_scores
    
    def bool_retrieval(self, query_terms1, query_terms2=[], operator=None):
        docs1 = self.free_form_retrieval(query_terms1)
        docs2 = self.free_form_retrieval(query_terms2)

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
        self.index = self.db.get_index_by_words([word1, word2])

        doc_scores = defaultdict(lambda: float)
        
        if (word1 not in self.index['word'].values) or (word2 not in self.index['word'].values):
            return doc_scores

        word1_docs = set(self.index[self.index['word']==word1]['article_id'].values)
        word2_docs = set(self.index[self.index['word']==word2]['article_id'].values)

        word1_doc_pos = {doc: np.asarray(self.index[(self.index['word']==word1)&(self.index['article_id']==doc)]['positions'].values[0]) for doc in word1_docs} 
        word2_doc_pos = {doc: np.asarray(self.index[(self.index['word']==word2)&(self.index['article_id']==doc)]['positions'].values[0]) for doc in word2_docs} 

        common_docs = word1_docs & word2_docs

        docs = set([])
        for p in range(1, proximity+1):
            docs = docs | self.__check_adjacent_words(common_docs, word1_doc_pos, word2_doc_pos, p).keys()

        for w in [word1, word2]:
            word_index = self.index[self.index['word']==w]
            for doc in docs:
                if doc not in doc_scores:
                    doc_scores[doc] = 0
                doc_scores[doc] += word_index[(word_index['word']==w)&(word_index['article_id']==doc)]['tfidf'].values[0]

        return doc_scores
    
    def __phrase_search(self, terms):
        if len(terms)==0:
            return set([])
        
        if len(terms)==1:
            return set(self.index[self.index['word'==terms[0]]]['article_id'])

        for i in range(0, len(terms)-1):
            term1 = terms[i]
            term2 = terms[i+1]

            if (term1 not in self.index['word'].values)|(term2 not in self.index['word'].values):
                return set([])
            
            if i==0:
                docs1 = set(self.index[self.index['word']==term1]['article_id'].values)
                term1_dict = {doc: np.asarray(self.index[(self.index['word']==term1)&(self.index['article_id']==doc)]['positions'].values[0]) for doc in docs1} 
            else:
                docs1 = set(output_dict.keys())
                term1_dict = output_dict
            docs2 = set(self.index[self.index['word']==term2]['article_id'].values)
            term2_dict = {doc: np.asarray(self.index[(self.index['word']==term2)&(self.index['article_id']==doc)]['positions'].values[0]) for doc in docs2} 
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

    query = 'usa'
    qtokenizer = QueryTokenizer()
    query_terms = qtokenizer.tokenize_free_form(query)

    r = Retrieval()
    ans = r.free_form_retrieval(query_terms)
    print(ans)
