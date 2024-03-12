import re
import pandas as pd
from nltk import PorterStemmer
from tqdm import tqdm
import timer
from tokenizer import Tokenizer

class Counter:
    def __init__(self, case_fold=True, stop=True,  stem=True ):
        self.tokenizer = Tokenizer( case_fold=case_fold, stop=stop,  stem=stem)
        
    def __preprocessing(self, line):
        return self.tokenizer.tokenize(line)
    def set_up_stopwords(self, filepath):
        pass


    def get_article_lengths(self, dataframe):
        self.article_lengths = {}

    # Assuming each row in your CSV represents a document, and the document text is in a column named 'text'
    # Adjust 'text' to match the actual column name in your CSV

        for row in dataframe.itertuples():  # Replace 'text' with the actual column name
            title = str(row.title) if row.title is not None else ""
            article = str(row.article) if row.article is not None else ""
            doc_no = row.article_id
            text = title+' '+article
            text = self.__preprocessing(text)
            self.article_lengths[doc_no] = len(text)
        # Convert the dictionary to a DataFrame
        self.article_lengths = pd.DataFrame(list(self.article_lengths.items()), columns=['article_id', 'doc_length'])
        return "lengths computed"
    def get_lengths(self):
        return self.article_lengths


