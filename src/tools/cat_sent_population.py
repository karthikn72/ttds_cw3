# Import the necessary classes
from database import Database
from timer import Timer
from category_predictor import CategoryPredictor
from sentiment_predictor import SentimentPredictor
import pandas as pd

def populate_category_and_sentiment(articles):
    db = Database()

    cat_predictor = CategoryPredictor('category')
    sent_predictor = SentimentPredictor('predicted_class')
    
    cat_predictor.load_model()
    sent_predictor.load_model()

    t = Timer('Populate category in {:.4f}s')
    t.start()

    cat_df = {
        'article_id': [],
        'section': []
    }

    cat_df = pd.DataFrame(cat_df)

    sent_df = {
        'article_id': [],
        'positive': [],
        'negative': [],
        'neutral': []
    }

    sent_df = pd.DataFrame(sent_df)

    for idx, row in articles.iterrows():
        title = row['title'] if row['title'] != None else ''
        article = row['article'] if row['article'] != None else ''
        content = title + '\n' + article

        cat_new_row = {
            'article_id': row['article_id'],
            'section': cat_predictor.predict(content)
        }

        cat_df = pd.concat([cat_df, pd.DataFrame([cat_new_row])], ignore_index=True)

        sent = sent_predictor(content)
        sent_new_row = {
            'article_id': row['article_id'],
            'positive': sent['Positive'],
            'negative': sent['Neg'],
            'neutral': sent['Neu']
        }

        sent_df = pd.concat([sent_df, pd.DataFrame([sent_new_row])], ignore_index=True)

    db.update_sections(cat_df)
    db.update_sentiments(sent_df)
    t.stop()