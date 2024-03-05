import re
from nltk.stem import PorterStemmer
import os

from spellchecker import SpellChecker

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
        return tokens
    
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
    

class QueryTokenizer(Tokenizer):
    def __init__(self, 
                 case_fold=True, 
                 stop=True, 
                 stop_file=DEFAULT_STOPWORD_FILE, 
                 stem=True, 
                 tokenize_re=DEFAULT_TOKENIZE_RULE):
        Tokenizer.__init__(self, case_fold, stop, stop_file, stem, tokenize_re)

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
                    processed.append(self.__tokenize_raw_query(query[open_quote:i]))
                    open_quote = -1
                    start = i+1
        processed = processed + self.__tokenize_raw_query(query[start:])
        return processed
    
    def tokenize_bool(self, query):
        parts = re.split(" +(AND|OR) +", query)

        term1 = parts[0] if len(parts)>=1 else []
        operator = parts[1] if len(parts)>=2 else None
        term2 = parts[2] if len(parts)>=3 else []

        term1_tokens = []
        if term1:
            term1_tokens = self.tokenize_free_form(term1)
 
        term2_tokens = []
        if term2:
            term2_tokens = self.tokenize_free_form(term2)

        return term1_tokens, term2_tokens, operator
    
    def process_word(self, word):
        return self.__tokenize_raw_query(word)[0]
    
    def __tokenize_raw_query(self, term):
        tokens = re.findall(pattern=self.tokenize_re, string=term)
        if self.case_fold:
            tokens = list(map(lambda x: x.lower(), tokens))
        if self.stop:
            tokens = self.stopping(tokens)
        tokens = self.__query_spell_correction(tokens)
        if self.stem:
            tokens = self.normalise(tokens)
        return tokens
    
    def __query_spell_correction(self, tokens):
        spell = SpellChecker()
        # find those words that may be misspelled
        misspelled_list = list(spell.unknown(tokens))
        # To keep the query order
        misspelled = [word for word in tokens if word in misspelled_list]
        new_query = []
        for word in tokens:
            if word not in misspelled:
                new_query.append(word)
            else:
                curr = spell.correction(word)
                new_query.append(curr)
        return new_query
 
    def __repr__(self):
        return f"QueryTokenizer(case_fold={self.case_fold}, stop={self.stop}, stop_file={self.stop_file}, stem={self.stem}, tokenize_re={self.tokenize_re})"


if __name__ == '__main__':
    q = QueryTokenizer()
    print(q.tokenize_bool('"middle east" AND pece')) # ([['middl', 'east']], ['piec'], 'AND')
    # print(q.tokenize_free_form('story book "middle east" piece "man America hunting"'))