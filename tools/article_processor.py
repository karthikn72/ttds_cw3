import pandas as pd
import re
pd.options.mode.chained_assignment = None

class ArticleProcessor:
    def __init__(self):
        pass
    
    def prep_authors(self, df):
        # Split authors into a list of authors
        df['author'] = df['author'].astype(str).apply(lambda x: x.split(', ')).apply(lambda x: "{" + ", ".join(x) + "}")
        return df

    def prep_date(self, df):
        df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
        df['date'] = df['date'].fillna(pd.to_datetime(df['date'].dt.date))
        return df

    def prep_article(self, df):
        df['article'] = df['article'].astype(str).apply(lambda x: re.sub(r'\{[^}]+\}', '', x)).apply(lambda x: x.replace('\n', '')).apply(lambda x: x.replace('\r', ''))
        df = df[df['article'].str.len() >= 500]
        return df

    def prep_title(self, df):
        df['title'] = df['title'].astype(str).apply(lambda x: x.replace('\n', '')).apply(lambda x: x.replace('\r', ''))
        # df['title'] = df['title'].apply(lambda x: x.replace('\r', ''))
        return df
    
    def prep_chunk(self, df, author=True, date=True, article=True, title=True):
        if author:
            df = self.prep_authors(df)
        if date:
            df = self.prep_date(df)
        if article:
            df = self.prep_article(df)
        if title:
            df = self.prep_title(df)
        return df