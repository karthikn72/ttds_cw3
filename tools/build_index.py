# Import the necessary classes
from database import Database
from indexer import Indexer
from timer import Timer
from cat_sent_population import populate_category_and_sentiment

def build_index(test=False, limit=1000):
    #prompt in terminal to ask if the user wants to reset the index
    fresh = input("Do you want to reset the index? (y/n) ")
    fresh = True if fresh.lower() == 'y' else False
    db = Database()
    N = db.num_articles()
    if fresh:
        db.reset_index()
    if test:
        N = 20000
    indexer = Indexer()
    indexer.set_up_stopwords('tools/resources/ttds_2023_english_stop_words.txt')

    t = Timer('Built index and updated sentiments and categories in {:.4f}s')
    t.start()
    for i in range(0, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)
        indexer.indexing(articles)
        print(f"--> Indexed {i + limit}/{N} documents")
        db.build_index(indexer.get_index())
        print(f"--> Added index for {i + limit}/{N} documents")
        # populate_category_and_sentiment(articles)
    t.stop()
    return "Indexing complete"

if __name__ == '__main__':
    build_index(test=True)
