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
        
        doc_scores = defaultdict(lambda: 0)
        for doc in docs:
            if doc not in doc_scores:
                doc_scores[doc] = 0
            doc_scores[doc] = docs1[doc]+docs2[doc]

        print(f'Length of boolean retrieved articles is {len(doc_scores)}')
        
        return doc_scores 
    
    def proximity_retrieval(self, word1, word2, proximity):
        print("Proximity retrieval called")
        self.index = self.db.get_index_by_words([word1, word2])

        doc_scores = defaultdict(lambda: 0)

        words_in_index = set(self.index['word'].unique())

        if len(self.index)==0 or len(words_in_index)!=2:
            return doc_scores
        
        if (word1 not in words_in_index) or (word2 not in words_in_index):
            return doc_scores

        index_w1 = self.index[self.index['word'] == word1]
        index_w2 = self.index[self.index['word'] == word2]

        word1_docs = set(self.index[self.index['word']==word1]['article_id'].unique())
        word2_docs = set(self.index[self.index['word']==word2]['article_id'].unique())

        # print("here")

        # common_docs = self.index.groupby('article_id').filter(lambda x: x['word'].nunique() > 1)['article_id'].unique()

        article_count = self.index['article_id'].value_counts()
        # print(article_count)
        common_docs = article_count[article_count == 2].index.tolist()
        # print(type(common_docs))
        # print(common_docs)

        # print(len(common_docs))

        # word1_doc_pos = {doc: np.asarray(self.index[(self.index['word']==word1)&(self.index['article_id']==doc)]['positions'].values[0]) for doc in common_docs} 
        # word2_doc_pos = {doc: np.asarray(self.index[(self.index['word']==word2)&(self.index['article_id']==doc)]['positions'].values[0]) for doc in common_docs} 

        # print("Common document gathered")

        # print(len(common_docs))

        docs = set([])

        start = time.time()

        common_docs = common_docs[:2000]

        for doc in common_docs:
            # print(doc)
            # print('here')
            fst_positions = index_w1[index_w1['article_id'] == doc]['positions'].tolist()[0]
            snd_positions = index_w2[index_w2['article_id'] == doc]['positions'].tolist()[0]
            # print(fst_positions)
            # print(snd_positions)
            # print('there')

            fst_idx = 0
            snd_idx = 0

            while fst_idx != len(fst_positions) and snd_idx != len(snd_positions):
                fst_pos = fst_positions[fst_idx]
                snd_pos = snd_positions[snd_idx]

                # print(fst_pos)
                # print(snd_pos)

                if abs(snd_pos - fst_pos) <= int(proximity):
                    docs.add(doc)
                    break
                elif snd_pos > fst_pos:
                    fst_idx += 1
                else:
                    snd_idx += 1

        t1 = time.time()

        print(f"Proximity retreival took {t1 - start} s")

        # for p in range(1, proximity+1):
        #     docs = docs | self.__check_adjacent_words(common_docs, word1_doc_pos, word2_doc_pos, p).keys()

        for doc in docs:
            if doc not in doc_scores:
                doc_scores[doc] = 0
            doc_scores[doc] += index_w1[index_w1['article_id'] == doc]['tfidf'].values[0]
            doc_scores[doc] += index_w2[index_w2['article_id'] == doc]['tfidf'].values[0]

        print(f'Length of proximity retrieved articles is {len(doc_scores)}')
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

    query = "(climate,change,19)"
    parts = query.strip("()").split(",")
    t1, t2, k = [part.strip() for part in parts]

    qtokenizer = QueryTokenizer()
    t1 = qtokenizer.process_word(t1)
    t2 = qtokenizer.process_word(t2)

    start_time = time.time()

    r = Retrieval()
    ans = r.proximity_retrieval(t1, t2, k)
    end_time = time.time()

    # Calculate elapsed time
    print('Time taken', end_time - start_time, 's')
    # print(ans)

