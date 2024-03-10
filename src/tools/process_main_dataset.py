import pandas as pd
import time
import os
import tqdm

import article_processor as AP

if __name__ == "__main__":
    chunksize = 10 ** 4
    in_file_path = 'dataset/all-the-news-2-1/all-the-news-2-1.csv'
    out_file_path = 'dataset/prepped_articles.csv'
    
    if os.path.exists(out_file_path):
        os.remove(out_file_path)

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
    chunks = pd.read_csv(in_file_path, chunksize=chunksize, usecols=use_cols, dtype=article_dtypes, low_memory=False)
    end_time = time.time()
    print(f"Time taken to read file: {end_time - start_time :.4f} seconds")
    
    ap = AP.ArticleProcessor()
    for (id, chunk) in tqdm.tqdm(enumerate(chunks), total=269, ncols=100):
        chunk = ap.prep(chunk, author=False, date=False)
        chunk.to_csv('dataset/prepped_articles.csv', mode='a', index=False, header=header)
        header = False