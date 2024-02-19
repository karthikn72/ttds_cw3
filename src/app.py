import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import time

from tools.tokenizer import QueryTokenizer
from tools.retrieval import TFIDFScoring
import tools.index_manager as im

app = Flask(__name__)
CORS(app)

# Load data
dataset_file = 'data/all-the-news-2-1.csv'
first_1k_docs = im.firstThousand(dataset_file)

class NotFoundError(Exception):
    pass

class BadRequestError(Exception):
    pass

def get_document_info(docid):
    doc = first_1k_docs.iloc[docid]
    title = doc['title']
    snippet = ' '.join(doc['article'].split()[:50]) #get the first 50 words of the article
    author = doc['author']
    url = doc['url']
    section = doc['section']
    date = doc['date']
    publication = doc['publication']
    return title, snippet, author, url, section, date, publication

def format_result(id , title, snippet, author, url, section, date, publication):
    return {
        'id': id,
        'title': title,
        'snippet': snippet,
        'author': author,
        'url': url,
        'section': section,
        'date': date,
        'publication': publication
    }

def get_status_code(results, error):
    if error:
        if isinstance(error, NotFoundError):
            return 404
        elif isinstance(error, BadRequestError):
            return 400
        else:
            return 500
    elif results:
        return 200
    else:
        return 204
    
def filter_unique(results):
    #for now lets define unique results by section (could be NaN) and date
    unique_results = []
    unique_keys = set()
    for result in results:
        key = str(result['section']) + result['date']
        if key not in unique_keys:
            unique_keys.add(key)
            unique_results.append(result)
    return unique_results

#get results based on search query
@app.route('/search', methods=['GET'])
def get_results():
    try:
        start_time = time.time()  #start timing query search time 
        search_query = request.args.get('query', '') # Get query from request

        if not search_query:
            raise BadRequestError("No search query provided")

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
            title, snippet, author, url, section, date, publication = get_document_info(docid)
            results.append(format_result(docid, title, snippet, author, url, section, date, publication))

        if not results:
            raise NotFoundError("No results found for the given query")
        
        unique_results = filter_unique(results)

        end_time = time.time()  #end timing
        retrieval_time = end_time - start_time  #to calculate retrieval time

        status = get_status_code(results, error=None)  #get status code

        #prepare response
        response = {
            'status': status,
            'retrieval_time': retrieval_time,
            'total_results': len(results),
            'total_unique_results': len(unique_results),
            'unique_results':unique_results,
            'results': results
        }

        return jsonify(response)

    except (BadRequestError, NotFoundError) as e:
        status = get_status_code(None, error=e)
        response = {
            'status': status,
            'message': str(e)
        }
        return jsonify(response)

if __name__ == '__main__':
    app.run()
