import pandas as pd
pd.options.mode.chained_assignment = None

import re
import time

def prep_authors(df):
    # Split authors into a list of authors
    df['author'] = df['author'].astype(str).apply(lambda x: x.split(', ')).apply(lambda x: "{" + ", ".join(x) + "}")
    return df

def prep_date(df):
    df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    df['date'] = df['date'].fillna(pd.to_datetime(df['date'].dt.date))
    return df

def prep_article(df):
    df['article'] = df['article'].astype(str).apply(lambda x: re.sub(r'\{[^}]+\}', '', x)).apply(lambda x: x.replace('\n', '')).apply(lambda x: x.replace('\r', ''))
    df = df[df['article'].str.len() >= 500]
    return df

def prep_title(df):
    df['title'] = df['title'].astype(str).apply(lambda x: x.replace('\n', '')).apply(lambda x: x.replace('\r', ''))
    # df['title'] = df['title'].apply(lambda x: x.replace('\r', ''))
    return df

if __name__ == "__main__":
    chunksize = 10 ** 4
    file_path = 'dataset/all-the-news-2-1/all-the-news-2-1.csv'
    article_df = pd.DataFrame()
    use_cols = ['date', 'author', 'title', 'article', 'url', 'publication']
    article_dtypes = {'date': 'str', 
                      'author': 'str', 
                      'title': 'str', 
                      'article': 'str', 
                      'url': 'str',
                      'publication': 'str'
                      }
    header = True
    
    start_time = time.time()
    chunks = pd.read_csv(file_path, chunksize=chunksize, usecols=use_cols, dtype=article_dtypes, low_memory=False)
    end_time = time.time()
    print(f"Time taken to read file: {end_time - start_time :.4f} seconds")

    start_time = time.time()
    for (id, chunk) in enumerate(chunks):
        start_time_chunk = time.time()
        chunk = prep_authors(chunk)
        chunk = prep_date(chunk)
        chunk = prep_article(chunk)
        chunk = prep_title(chunk)
        chunk.to_csv('dataset/prepped_articles.csv', mode='a', index=False, header=header)
        header = False
        end_time_chunk = time.time()
        print(f"Processed chunk {id}: {end_time_chunk - start_time_chunk :.4f} seconds")
    end_time = time.time()
    print(f"Total time for all chunks: {end_time - start_time :.4f} seconds")