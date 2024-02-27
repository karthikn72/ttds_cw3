import re
from nltk.stem import PorterStemmer
import os

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

    def __tokenize_term(self, term):
        tokens = re.findall(pattern=self.tokenize_re, string=term)
        if self.case_fold:
            tokens = list(map(lambda x: x.lower(), tokens))
        if self.stop:
            tokens = self.stopping(tokens)
        if self.stem:
            tokens = self.normalise(tokens)
        return tokens

    def tokenize(self, query):
        parts = re.split(" +(AND|OR) +", query)

        term1 = parts[0] if len(parts)>=1 else []
        operator = parts[1] if len(parts)>=2 else None
        term2 = parts[2] if len(parts)>=3 else []

        term1_tokens = []
        if term1:
            if term1[0]=='"' and term1[-1]=='"':
                term1_tokens = [" "] + self.__tokenize_term(term1[1:-1])
            else:
                term1_tokens = self.__tokenize_term(term1)
 
        term2_tokens = []
        if term2:
            if term2[0]=='"' and term2[-1]=='"':
                term2_tokens = [" "] + self.__tokenize_term(term2[1:-1])
            else:
                term2_tokens = self.__tokenize_term(term2)

        return term1_tokens, term2_tokens, operator 
 
    def __repr__(self):
        return f"QueryTokenizer(case_fold={self.case_fold}, stop={self.stop}, stop_file={self.stop_file}, stem={self.stem}, tokenize_re={self.tokenize_re})"


if __name__ == '__main__':
    q = QueryTokenizer()
    print(q.tokenize('"middle east" AND peace'))