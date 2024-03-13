# Import the necessary classes
from database import Database
from indexer import Indexer
from timer import Timer
# from cat_sent_population import populate_category_and_sentiment

def build_index(test=False, start=0, limit=10000, fresh=False):
    #prompt in terminal to ask if the user wants to reset the index
    db = Database()
    N = db.num_articles()
    if fresh:
        db.reset_index()
    if test:
        N = 20000
    indexer = Indexer()
    indexer.set_up_stopwords('tools/resources/ttds_2023_english_stop_words.txt')

    t = Timer('---> Built index in {:.4f}s')
    t.start()
    for i in range(start, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)
        indexer.indexing(articles)
        print(f"--> Locally indexed {i + limit}/{N} articles")
        db.build_index(indexer.get_index())
        print(f"--> Added index to DB for {i + limit}/{N} articles")
        # populate_category_and_sentiment(articles, sent_scores=True)
        # print(f"--> Added index for {i + limit}/{N} documents")
    t.stop()
    return "Indexing complete"

if __name__ == '__main__':
    build_index(test=False, start=850000)
