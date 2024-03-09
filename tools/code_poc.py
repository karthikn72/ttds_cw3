import re
import pandas as pd
from nltk import PorterStemmer
from tqdm import tqdm
import timer

class Tester:
    def __init__(self) -> None:
        self.stemmer = PorterStemmer()
        self.stopwords = set()
        
        pass
    def set_up_stopwords(self, filepath):
        with open(filepath) as stopFile:
            self.stopwords = set(stopFile.read().splitlines())
    


    def preprocessing(self, line, stopping=True, stemming=True):
        line = line.replace('\'', ' ')
        line = line.replace('-', ' ')
        pattern = re.compile('[a-zA-Z0-9 \n]+')
        result = ''.join(pattern.findall(re.sub('\n', ' ', line.lower())))
        if stopping and stemming:
            filtered_lines = [self.stemmer.stem(word) for word in result.split() if word not in self.stopwords]
        elif stopping:
            filtered_lines = [word for word in result.split() if word not in self.stopwords]
        elif stemming:
            filtered_lines = [self.stemmer.stem(word) for word in result.split()]
        else:
            filtered_lines = [word for word in result.split()]
        return ' '.join(filtered_lines).rstrip()
    def get_article_lengths(self, file_path):
        # File is a massive csv, open by chunks
        chunksize = 10 ** 5
        article_lengths = {}
        counter = 0
        doc_no = 1
        timer1 = timer.Timer("10000 processed in: {:0.4f} seconds")
        
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            # Assuming each row in your CSV represents a document, and the document text is in a column named 'text'
            # Adjust 'text' to match the actual column name in your CSV
            timer1.start()
            for row in chunk.itertuples():  # Replace 'text' with the actual column name
                
                title = str(row.title) if row.title is not None else ""
                article = str(row.article) if row.article is not None else ""
                text = title+' '+article
                text = self.preprocessing(text)
                article_lengths[doc_no] = len(text.split())
                doc_no += 1
                
                #kill process with exception
            timer1.stop()
            #dump the table if the df becomes too big

            
            
            
            
                    
            counter += 1
            print(f'Processed {len(article_lengths)} documents')

        # Convert the dictionary to a DataFrame
        df_article_lengths = pd.DataFrame(list(article_lengths.items()), columns=['doc_id', 'doc_length'])
        print(df_article_lengths)
        
        return df_article_lengths



if __name__ == '__main__':
    idxer = Tester()
    idxer.set_up_stopwords('resources/ttds_2023_english_stop_words.txt')
    idxer.get_article_lengths('dataset/all-the-news-2-1.csv')
    print('done')
    