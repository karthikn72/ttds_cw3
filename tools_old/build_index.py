# Import the necessary classes
from database import Database
from indexer import Indexer
from timer import Timer
from cats_sent_population import populate_category_and_sentiment

def build_index(test=False, limit=1000):
    #prompt in terminal to ask if the user wants to reset the index
    fresh = input("Do you want to reset the index? (y/n) ")
    fresh = True if fresh.lower() == 'y' else False
    db = Database()
    N = db.num_articles()
    if fresh:
        db.reset_index()
    if test:
        N = 10000
    indexer = Indexer()
    indexer.set_up_stopwords('tools/resources/ttds_2023_english_stop_words.txt')

    t = Timer('Built index in {:.4f}s')
    t.start()
    for i in range(0, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)
        indexer.indexing(i, articles)

        populate_category_and_sentiment(articles)

        print(f"--> Indexed {i + limit}/{N} documents")
        db.build_index(indexer.get_index())
        print(f"--> Added index for {i + limit}/{N} documents")
    t.stop()
    return "Indexing complete"

def build_index_aao():
    db = Database()
    N = db.num_articles()
    counter = 0
    indexer = Indexer()
    indexer.set_up_stopwords('resources/ttds_2023_english_stop_words.txt')
    while counter < N:
        articles = db.get_articles(limit=1000)
        indexer.indexing_aao(articles, counter)
        counter += 1000
    db.build_index(indexer.get_index())
    del indexer
    return "Indexing complete"

if __name__ == '__main__':
    build_index(test=True)
