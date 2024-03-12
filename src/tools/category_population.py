# Import the necessary classes
from database import Database
from timer import Timer
from category_predictor import CategoryPredictor
import pandas as pd

def populate_category(limit=1000):
    db = Database()
    N = 2000

    cat_predictor = CategoryPredictor('category')
    cat_predictor.load_model()

    t = Timer('Populate category in {:.4f}s')
    t.start()

    for i in range(0, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)
        articles.fillna("", inplace=True)

        articles['text'] = articles['title'] + '\n' + articles['article'][:400]

        article_df = pd.DataFrame(columns=['text'])

        # print(articles['text'])
        texts = pd.DataFrame(articles['text'])

        cat_df = pd.DataFrame(columns=['section'])
        cat_df['section'] = cat_df['section'].tolist() + cat_predictor.predict(texts)

        df = pd.concat([articles['article_id'], cat_df['section']], axis=1)

        # print('done')

        # print(df)
        db.update_sections(cat_df)
        df = df.drop(df.index)
    t.stop()

if __name__ == '__main__':
    populate_category(100)
