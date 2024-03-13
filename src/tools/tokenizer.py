import re
from nltk.stem import PorterStemmer
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from tools.query_expansion import QueryExpander

from autocorrect import Speller

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))

DEFAULT_STOPWORD_FILE = os.path.join(MODULE_DIR, 'resources', 'ttds_2023_english_stop_words.txt')
DEFAULT_TOKENIZE_RULE = r'\w+'

class Tokenizer:
    def __init__(self, 
                 case_fold=True, 
                 stop=True, 
                 stop_file=DEFAULT_STOPWORD_FILE, 
                 stem=True, 
                 tokenize_re=DEFAULT_TOKENIZE_RULE):
        self.case_fold = case_fold
        self.stop = stop
        self.stop_file = stop_file
        self.stem = stem
        self.tokenize_re = tokenize_re
    
    def tokenize(self, line):
        tokens = re.findall(pattern=self.tokenize_re, string=line)
        if self.case_fold:
            tokens = list(map(lambda x: x.lower(), tokens))
        if self.stop:
            tokens = self.stopping(tokens)
        if self.stem:
            tokens = self.normalise(tokens)
        return [token for token in tokens if len(token) < 255]
    
    # Remove stop words
    def stopping(self, tokens):
        with open(self.stop_file, "r") as stop_word_doc:
            stop_words = set(stop_word_doc.read().split('\n')[:-1])
            tokens = [token for token in tokens if token not in stop_words]
        return tokens

    # Normalise tokens
    def normalise(self, tokens):
        stemmer = PorterStemmer()
        tokens = list(map(stemmer.stem, tokens))
        return tokens
    
    def __repr__(self):
        return f"Tokenizer(case_fold={self.case_fold}, stop={self.stop}, stop_file={self.stop_file}, stem={self.stem}, tokenize_re={self.tokenize_re})"



''' 
Usage Examples:
q = QueryTokenizer()

1. Free form queries - query
    * These queries include a combination of words and phrases of any length.
    * Eg: 'story book "middle east" piece "man America hunting"'
    * q.tokenize_free_form(query) - returns a list of tokens, grouping phrases within the query into a list
    * Output Eg: ['stori', 'book', ['middl', 'east'], 'piec', ['man', 'america', 'hunt']]
                also returns expanded query => ['narr', 'narrat', 'tale', 'adult', 'male']
    * Raises - ValueError, when query after processing is empty

2. Boolean queries - operand1, operand2, operator
    * These queries have 2 free form queries combined by a boolean operator (AND/OR)
    * Eg: 'story book "middle east"' AND 'call denver direct'
    * To tokenize:
        query_tokens1, expanded_query_tokens1 = q.tokenize_free_form(operand1)
        query_tokens2, expanded_query_tokens2 = q.tokenize_free_form(operand2)

3. Proximity search queries - word1, word2, proximity
    * These queries have 2 words and proximity param of the words
    * To tokenize:
        processed_word1 = q.process_word(word1)
        processed_word2 = q.process_word(word2)
    * Raises - ValueError, when word is polluted with non-alphanum chars, and when word is a stop word
    * Make sure to check if proximity is > 0 in the API before calling the retrieval function.

'''
class QueryTokenizer(Tokenizer):
    def __init__(self, 
                 case_fold=True, 
                 stop=True, 
                 stop_file=DEFAULT_STOPWORD_FILE, 
                 stem=True, 
                 tokenize_re=DEFAULT_TOKENIZE_RULE):
        Tokenizer.__init__(self, case_fold, stop, stop_file, stem, tokenize_re)
        self.qe = QueryExpander()

    def tokenize_free_form(self, query):
        open_quote = -1
        start = 0
        processed = []
        for i in range(len(query)):
            if query[i]=='"':
                if open_quote==-1:
                    processed = processed + self.__tokenize_raw_query(query[start:i])
                    open_quote=i+1
                    start = i+1
                else:
                    processed_phrase = self.__tokenize_raw_query(query[open_quote:i])
                    if processed_phrase:
                        processed.append(processed_phrase)
                    open_quote = -1
                    start = i+1
        processed = processed + self.__tokenize_raw_query(query[start:])
        if processed==[]:
            raise ValueError("Query seems to contain no specific keywords.")
        return processed, self.__query_expansion(query)
    
    def process_word(self, word):
        processed = self.__tokenize_raw_query(word)
        if processed==[]:
            raise ValueError("Word seems to not be a specific keyword.")
        if len(processed)>1:
            raise ValueError("Word seems to contain special characters.")
        return processed[0]
    
    def __tokenize_raw_query(self, term, should_stem=True):
        tokens = re.findall(pattern=self.tokenize_re, string=term)
        if self.case_fold:
            tokens = list(map(lambda x: x.lower(), tokens))
        if self.stop:
            tokens = self.stopping(tokens)
        tokens = self.__query_spell_correction(tokens)
        if self.stem and should_stem:
            tokens = self.normalise(tokens)
        return tokens
    
    def __query_spell_correction(self, tokens):
        spell = Speller(lang='en')
        correct_tokens = list(spell.existing(tokens))

        corrected_query = []
        for word in tokens:
            if word in correct_tokens:
                corrected_query.append(word)
            else:
                corrected_word = spell(word)
                if corrected_word != word:
                    corrected_query.append(corrected_word)

        return corrected_query
 
    def __query_expansion(self, query):
        tokenized = self.__tokenize_raw_query(query, False)
        expanded_query = self.qe.expand_query(tokenized)
        expanded_query = list(filter(lambda word : not re.compile(r'[^a-zA-Z0-9]').search(word), expanded_query))
        if self.stop:
            expanded_query = self.stopping(expanded_query)
        if self.stem:
            expanded_query = self.normalise(expanded_query)
        return expanded_query

    def __repr__(self):
        return f"QueryTokenizer(case_fold={self.case_fold}, stop={self.stop}, stop_file={self.stop_file}, stem={self.stem}, tokenize_re={self.tokenize_re})"


if __name__ == '__main__':
    q = QueryTokenizer()
    # print(q.tokenize_bool('"middle east" AND pece')) # ([['middl', 'east']], ['piec'], 'AND')
    print(q.tokenize_free_form('story book "middle east" piece "man America hunting"'))
    # print(q.tokenize_free_form('story book "middle east" piece "man America hunting"'))
