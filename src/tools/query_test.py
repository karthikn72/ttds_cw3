
from retrieval_2 import Retrieval


if __name__ == '__main__':
    r = Retrieval('index/index_tfidf.pkl')
    print(r.get_query_docs('call denver direct'))
    print(r.get_index("0"))