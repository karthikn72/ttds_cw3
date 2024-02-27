# Import the necessary classes
from database import Database
from indexer import Indexer

def build_index(test=False, fresh=False):
    
    db = Database()
    N = db.num_articles()
    if fresh:
        db.reset_index()
    if test:
        N = 1000
    counter = 0
    indexer = Indexer()
    indexer.set_up_stopwords('resources/ttds_2023_english_stop_words.txt')
    while counter < N:
        articles = db.get_articles(limit=1000,offset=counter)
        indexer.indexing(articles, counter)
        print(f"Indexed {counter+1000} documents")
        db.build_index(indexer.get_index())
        print(f"Successfully built {counter+1000}")
        counter += 1000
    del indexer
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
