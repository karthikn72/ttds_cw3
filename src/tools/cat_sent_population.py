# Import the necessary classes
from database import Database
from timer import Timer
from category_predictor import CategoryPredictor
from sentiment_predictor import SentimentPredictor
import pandas as pd

def populate_category_and_sentiment(articles, sent_scores=False):
    db = Database()

    cat_predictor = CategoryPredictor('category')
    sent_predictor = SentimentPredictor('predicted_class')
    
    cat_predictor.load_model()
    sent_predictor.load_model()

    t = Timer('Populate category in {:.4f}s')
    t.start()

    
    articles.fillna("", inplace=True)
    articles['text'] = articles['title'] + '\n' + articles['article'][:400]

    texts = pd.DataFrame(articles['text'])

    cat_df = pd.DataFrame(columns=['section'])
    cat_df['section'] = cat_predictor.predict(texts)

    cat_df = pd.concat([articles['article_id'], cat_df['section']], axis=1)


    db.update_sections(cat_df)
    if sent_scores:
        sent_df = pd.DataFrame(columns=['positive', 'negative', 'neutral'])
        sent_pred_scores = sent_predictor.predict_scores(texts)
        print(sent_pred_scores.columns)
        print(sent_pred_scores)
        sent_df['positive'] = sent_pred_scores['Positive']
        sent_df['negative'] = sent_pred_scores['Neg']
        sent_df['neutral'] = sent_pred_scores['Neu']

        sent_df = pd.concat([articles['article_id'], sent_df], axis=1)

        db.update_sentiment_scores(sent_df)
    else:
        # To be implement to update only a single sentiment
        sent_df = pd.DataFrame(columns=['sentiment'])

        sent_df['sentiment'] = sent_predictor.predict_sentiment(texts)

        sent_df = pd.concat([articles['article_id'], sent_df], axis=1)

        db.update_sentiments(sent_df)
    t.stop()
