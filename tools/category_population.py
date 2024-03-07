# Import the necessary classes
from database import Database
from timer import Timer
from category_predictor import CategoryPredictor
import pandas as pd

def populate_category(limit=1000):
    db = Database()
    N = 10000

    predictor = CategoryPredictor('category')
    predictor.load_model()

    t = Timer('Populate category in {:.4f}s')
    t.start()
    df = {
        'article_id': [],
        'section': []
    }
    for i in range(0, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)
        for idx, row in articles.iterrows():
            new_row = {
                'article_id': row['article_id'],
                'section': predictor.predict(row['title'] + '\n' + row['article'])
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        db.update_sections(df)
        df = df.drop(df.index)
    t.stop()
