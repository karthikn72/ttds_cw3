import database
from tokenizer import QueryTokenizer
from retrieval import Retrieval
import heapq

def search(query, query2='', operator='', type='free_form'):
    db = database.Database()

    if type=='free_form':
        qtokenizer = QueryTokenizer()
        query_terms, expanded_query = qtokenizer.tokenize_free_form(query)
        print(query_terms, expanded_query)

        r = Retrieval()
        ans = r.free_form_retrieval(query_terms, expanded_query)
        top5 = list(heapq.nlargest(5, ans, key=ans.get))

        for x in top5:
            print(x, ans[x])
        
        print(db.get_articles(article_ids=top5).title.values)

    elif type=='bool':
        qtokenizer = QueryTokenizer()
        query_terms1, expanded_query1 = qtokenizer.tokenize_free_form(query)
        query_terms2, expanded_query2 = qtokenizer.tokenize_free_form(query2)

        print(query_terms1, expanded_query1, query_terms2, expanded_query2)

        r = Retrieval()
        ans = r.bool_retrieval(query_terms1, expanded_query1, query_terms2, expanded_query2, operator)
        top5 = list(heapq.nlargest(5, ans, key=ans.get))

        for x in top5:
            print(x, ans[x])
        
        print(db.get_articles(article_ids=top5).title.values)
        
query = '"climate change"'
search(query)

# db = database.Database()

# flat_list = []
# for row in query_terms:
#     if type(row)==list:
#         flat_list.extend(row)
#     else:
#         flat_list.append(row)

# print(query_terms)
# index = db.get_index_by_words(flat_list)
# print(index)

# sorted_index = index.sort_values(by='tfidf', ascending=False)
# print(sorted_index)

# top5 = list(sorted_index.article_id.values[:5])
# print(db.get_articles(article_ids=top5).title.values)
