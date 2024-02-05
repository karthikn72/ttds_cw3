import re
from nltk.stem import PorterStemmer
import os

MODULE_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_STOPWORD_FILE = os.path.join(MODULE_DIR, "resources/ttds_2023_english_stop_words.txt")
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

    # Tokenize queries
    def tok_query(self, query):
        window_size = 0
        query_tokens = []
        bool_op = None

        window_re = r'\#(\d+)\(([a-zA-Z0-9, "]+)\)'
        
        if re.search(window_re, query):
            print("Window search")
            [(win_size, q)] = re.findall(window_re, query)
            window_size = int(win_size)
            [q1, q2] = q.split(',')
            query_tokens = [(1, self.tokenize(q1)), (1, self.tokenize(q2))]
        
        elif " AND " in query:
            print("AND Search")
            bool_op = "and"
            print(query.split("AND"))
            for q in [x.strip() for x in query.split(" AND ")]:
                print(q)
                flag = 1
                if "NOT " in q:
                    flag = 0
                    q = ' '.join(q.split()[1:])
                query_tokens.append((flag, self.tokenize(q)))
        
        elif " OR " in query:
            print("OR Search")
            bool_op = "or"
            for q in [x.strip() for x in query.split(" OR ")]:
                flag = 1
                if "NOT " in q:
                    flag = 0
                    q = ' '.join(q.split()[1:])
                query_tokens.append((flag, self.tokenize(q)))
        else:
            query_tokens.append((1, self.tokenize(query)))
            
        q_dict = {"query_tokens":query_tokens, "window_size":window_size, "bool_op":bool_op} 

        return q_dict

    def __repr__(self):
        return f"QueryTokenizer(case_fold={self.case_fold}, stop={self.stop}, stop_file={self.stop_file}, stem={self.stem}, tokenize_re={self.tokenize_re})"