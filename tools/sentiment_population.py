# Import the necessary classes
from database import Database
from timer import Timer
from sentiment_predictor import SentimentPredictor
import pandas as pd

def populate_sentiment(limit=1000):
    db = Database()
    N = 10000

    predictor = SentimentPredictor('predicted_class')
    predictor.load_model()

    t = Timer('Populate sentiment in {:.4f}s')
    t.start()
    df = {
        'article_id': [],
        'positive': [],
        'negative': [],
        'neutral': []
    }
    for i in range(0, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)
        for idx, row in articles.iterrows():
            title = row['title'] if row['title'] != None else ''
            article = row['article'] if row['article'] != None else ''
            content = title + '\n' + article

            sent = predictor.predict(content)
            new_row = {
                'article_id': row['article_id'],
                'positive': sent['Positive'],
                'negative': sent['Neg'],
                'neutral': sent['Neu']
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        db.update_sentiments(df)
        df = df.drop(df.index)
    t.stop()