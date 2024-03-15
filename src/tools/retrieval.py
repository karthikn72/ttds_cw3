from collections import defaultdict
import heapq
import pickle
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from tools.database import Database
import pandas as pd
import time

import numpy as np

from tools.tokenizer import Tokenizer, QueryTokenizer

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

    def free_form_retrieval(self, query_terms, expanded_query):
        start = time.time()
        self.index = self.db.get_index_by_words(self.__flatten_query_terms(query_terms))

        if len(self.index)==0 or len(self.index.article_id.unique())<=20:
            index_expanded = self.db.get_index_by_words(expanded_query)
            self.index = pd.concat([self.index, index_expanded], axis=0)

        t1 = time.time()
        print('Time taken to retrieve index (including expanded query)', t1-start)
        start = t1
        
        doc_scores = defaultdict(lambda: 0)

        if len(self.index)==0:
            return doc_scores

        query_words = list(filter(lambda x: type(x)==str, query_terms))
        
        doc_scores = self.__bow_retrieval(query_words, doc_scores)
        doc_scores = self.__bow_retrieval(expanded_query, doc_scores, 0.5)

        t1 = time.time()
        print('To retrieve docs and scores for non-phrase terms', t1-start)
        start = t1

        query_phrases = list(filter(lambda x: type(x)==list, query_terms))

        if len(query_phrases)>0:
            phrase_docs = set([])
            docs_have_phrases = list(map(lambda x: self.__phrase_search(x), query_phrases))
        
            for x in docs_have_phrases:
                if len(phrase_docs)==0:
                    phrase_docs = x
                else:
                    phrase_docs = phrase_docs & x
        
            phrase_words = set(self.__flatten_query_terms(query_phrases))

            phrase_docs_scores = self.index[(self.index['word'].isin(phrase_words)) & (self.index['article_id'].isin(phrase_docs))].groupby('article_id').sum()['tfidf'].to_dict()  

            for d in doc_scores:
                if d in phrase_docs:
                    phrase_docs_scores[d]+=doc_scores[d]

            doc_scores = phrase_docs_scores

            t1 = time.time()
            print('Phrase searches', t1-start)
            start = t1

        print(f'Length of retrieved articles is {len(doc_scores)}')

        return doc_scores

    def __bow_retrieval(self, query_words, doc_scores, weight=1):
        start = time.time()
        new_doc_scores = self.index[(self.index['word'].isin(query_words))].groupby('article_id').sum()['tfidf'].to_dict()
        for doc in new_doc_scores:
            if doc in doc_scores:
                doc_scores[doc] += new_doc_scores[doc]*weight
            else:
                doc_scores[doc] = new_doc_scores[doc]*weight
        t1 = time.time()
        print(f'Free words search {query_words}', t1-start)
        start = t1

        return doc_scores
    
    def bool_retrieval(self, query_terms1, expanded_query1, query_terms2=[], expanded_query2=[], operator=None):
        docs1 = self.free_form_retrieval(query_terms1, expanded_query1)
        docs2 = self.free_form_retrieval(query_terms2, expanded_query2)

        if operator == 'AND':
            docs = docs1.keys() & docs2.keys()
        else:
            docs = docs1.keys() | docs2.keys()
        
        docs_scores = defaultdict(lambda: 0)
        for doc in docs:
            if doc not in docs_scores:
                docs_scores[doc] = 0
            docs_scores[doc] = docs1[doc]+docs2[doc]

        print(f'Length of retrieved articles is {len(doc_scores)}')
        
        return docs_scores 
    
    def proximity_retrieval(self, word1, word2, proximity):
        self.index = self.db.get_index_by_words([word1, word2])

        doc_scores = defaultdict(lambda: 0)

        if len(self.index)==0 or len(self.index['word'].unique())!=2:
            return doc_scores
        
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

        print(f'Length of retrieved articles is {len(doc_scores)}')
        return doc_scores
    
    def __phrase_search(self, terms):
        if len(terms)==0:
            return set([])
        
        if len(terms)==1:
            return set(self.index[self.index['word']==terms[0]]['article_id'])

        for i in range(0, len(terms)-1):
            term1 = terms[i]
            term2 = terms[i+1]

            if (term1 not in self.index['word'].values)|(term2 not in self.index['word'].values):
                return set([])

            term1_index = self.index[self.index['word']==term1]
            term2_index = self.index[self.index['word']==term2]
            
            if i==0:
                docs1 = set(term1_index['article_id'].unique())
                term1_dict = dict(zip(term1_index['article_id'], term1_index['positions']))
                # term1_dict = {doc: self.index[(self.index['word']==term1)&(self.index['article_id']==doc)]['positions'].values[0] for doc in docs1} 
            else:
                docs1 = set(output_dict.keys())
                term1_dict = output_dict
            docs2 = set(term2_index['article_id'].unique())
            term2_dict = dict(zip(term2_index['article_id'], term2_index['positions']))
            # term2_dict = {doc: np.asarray(self.index[(self.index['word']==term2)&(self.index['article_id']==doc)]['positions'].values[0]) for doc in docs2} 
            shared_docs = docs1 & docs2
            
            output_dict = self.__check_adjacent_words(shared_docs, term1_dict, term2_dict)

            if len(output_dict)==0:
                return set([])
        
        return set(output_dict.keys())
    
    def __check_adjacent_words(self, shared_docs, former_pos_dict, later_pos_dict, proximity=1):
        output_dict = defaultdict(list)
        for doc in shared_docs:
            term1_positions = np.array(former_pos_dict[doc]) + proximity
            term2_positions = np.array(later_pos_dict[doc])

            phrase_pos = np.intersect1d(term1_positions, term2_positions)

            if len(phrase_pos) > 0:
                output_dict[doc] = phrase_pos
            
        return dict(output_dict)
    
if __name__ == '__main__':

    query = "\"germanys merkel backs foreign ministers\""
    qtokenizer = QueryTokenizer()
    query_terms, expanded_query = qtokenizer.tokenize_free_form(query)

    start_time = time.time()

    r = Retrieval()
    ans = r.free_form_retrieval(query_terms, expanded_query)
    end_time = time.time()

    # Calculate elapsed time
    print('Time taken', end_time - start_time, 's')
    # print(ans)

