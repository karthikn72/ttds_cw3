import database
from tokenizer import QueryTokenizer
from retrieval import Retrieval
import heapq

db = database.Database()

query = 'sochi'
qtokenizer = QueryTokenizer()
query_terms = qtokenizer.tokenize_free_form(query)

flat_list = []
for row in query_terms:
    if type(row)==list:
        flat_list.extend(row)
    else:
        flat_list.append(row)

print(query_terms)
index = db.get_index_by_words(flat_list)
print(index)
sorted_index = index.sort_values(by='tfidf', ascending=False)

print(sorted_index)

top5 = list(sorted_index.article_id.values[:5])

# r = Retrieval()
# ans = r.free_form_retrieval(query_terms)


# top5 = list(heapq.nlargest(5, ans, key=ans.get))

print(list(sorted_index.article_id.values[:5]))
print(db.get_articles(article_ids=top5)[['article_id','title']])