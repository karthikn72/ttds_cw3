# Import the necessary classes
from database import Database
from doc_counter import Counter
from timer import Timer



def build_doc_table(test=True, limit=1000, fresh=True):
    #prompt in terminal to ask if the user wants to reset the index
    db = Database()
    N = db.num_articles()
    if fresh:
        db.reset_doc_length_table()
    if test:
        N = 20000
    counter = Counter()

    t = Timer('Built Document Length Table in {:.4f}s')
    t.start()
    for i in range(0, N + 1, limit):
        articles = db.get_articles(limit=limit,offset=i)
        counter.article_lengths(articles)
        print(f"--> {i + limit}/{N} documents")
        db.build_doc_length_table(counter.get_lengths())
        print(f"--> Added for {i + limit}/{N} documents")
        # populate_category_and_sentiment(articles)
    t.stop()
    return "Indexing complete"

if __name__ == '__main__':
    build_doc_table(test=True, fresh=True)
