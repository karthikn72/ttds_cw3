import sys
import os
from flask import Flask, request
from flask_cors import CORS
import pandas as pd

from tools.tokenizer import QueryTokenizer
from tools.retrieval import TFIDFScoring
import tools.index_manager as im

app = Flask(__name__)
CORS(app)

# Load data
dataset_file = 'data/all-the-news-2-1.csv'
first_1k_docs = im.firstThousand(dataset_file)

def get_title(docid):
    return first_1k_docs.iloc[docid]['title']

def get_snippet(docid):
    # get first 50 words of article
    return ' '.join(first_1k_docs.iloc[docid]['article'].split()[:50])

def format_result(id , title, snippet):
    return {
        'id': id,
        'title': title,
        'snippet': snippet
    }

#get results based on search query
@app.route('/search', methods=['GET'])
def get_results():
    search_query = request.args.get('query''' , '') # Get query from request

    #tokenize query
    qtokenizer = QueryTokenizer()
    query_tokens = qtokenizer.tokenize(search_query)

    #use score function to get docids
    r = TFIDFScoring(index_filename='tools/index.txt')
    scores = r.score(query_tokens)
    docids = [score[0] for score in scores]

    #get results
    results = []
    for docid in docids:
        title = get_title(docid)
        snippet = get_snippet(docid)
        results.append(format_result(docid, title, snippet))

    return {'results': results}

if __name__ == '__main__':
    app.run()
