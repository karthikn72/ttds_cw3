# Import the necessary classes
from database import Database
from indexer import Indexer

def build_index():
    db = Database()
    db.connect_with_connector()
    N = db.get_num_articles()
    counter = 0
    indexer = Indexer()
    indexer.set_up_stopwords('resources/ttds_2023_english_stop_words.txt')
    while counter < N:
        articles = db.get_articles(limit=1000)
        indexer.indexing(articles, counter)
        db.build_index(indexer.get_index())
        counter += 1000
    del indexer
    return "Indexing complete"

def build_index_aao():
    db = Database()
    db.connect_with_connector()
    N = db.get_num_articles()
    
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
    build_index()
