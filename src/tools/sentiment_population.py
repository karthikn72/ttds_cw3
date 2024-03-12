# Import the necessary classes
from database import Database
from timer import Timer
from sentiment_predictor import SentimentPredictor
import pandas as pd

def populate_sentiment(limit=1000, sent_scores=False):
    db = Database()
    N = 10000

    sent_predictor = SentimentPredictor('predicted_class')
    sent_predictor.load_model()

    t = Timer('Populate sentiment in {:.4f}s')
    t.start()

    for i in range(0, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)

        articles.fillna("", inplace=True)

        articles['text'] = articles['title'] + '\n' + articles['article'][:400]

        article_df = pd.DataFrame(columns=['text'])

        print(articles['text'])
        texts = pd.DataFrame(articles['text'])

        if sent_scores:
            sent_df = pd.DataFrame(columns=['positive', 'negative', 'neutral'])
            sent_pred_scores = sent_predictor.predict_scores(texts)

            sent_df['positive'] = sent_pred_scores['Positive']
            sent_df['negative'] = sent_pred_scores['Neg']
            sent_df['neutral'] = sent_pred_scores['Neu']

            sent_df = pd.concat([articles['article_id'], sent_df], axis=1)

            # db.update_sentiment_scores(sent_df)
            sent_df = sent_df.drop(sent_df.index)
        else:
            # To be implement to update only a single sentiment
            sent_df = pd.DataFrame(columns=['sentiment'])

            sent_df['sentiment'] = sent_predictor.predict_sentiment(texts)

            sent_df = pd.concat([articles['article_id'], sent_df], axis=1)

            # print(sent_df)
            db.update_sentiments(sent_df)
            sent_df = sent_df.drop(sent_df.index)
    t.stop()

if __name__ == '__main__':
    populate_sentiment(10, sent_scores=False)