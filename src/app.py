import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import time
import threading
from datetime import datetime

from tools.tokenizer import Tokenizer, QueryTokenizer
from tools.retrieval import TFIDFScoring
from tools.retrieval_2 import Retrieval
from tools.database import Database

app = Flask(__name__)
CORS(app, origins=["https://sentinews-413116.nw.r.appspot.com/"])

# Load database
db = Database()

#process parameters
def process_params(request_args):
    multi_params = ["sentiment", "author", "publication", "category"]
    single_params = ["query", "sortBy", "type", "page", "request"] 
    exception_params = ["from", "to"] #these are date params

    processed_params = {}

    # Retrieve the arguments for each parameter and check if they are not empty and alphanumeric
    for param in multi_params:
        values = sorted(request_args.getlist(param))
        for value in values:
            if value == "" or not re.match("^[a-zA-Z0-9_ ]*$", value):
                return {'error': {'status': 400, 'message': f'Invalid value: {value} for parameter: {param}'}}
        processed_params[param] = values #group up values by param (multi values for each param)

    for param in single_params:
        values = request_args.getlist(param)
        for value in values:
            if value == "" or not re.match("^[a-zA-Z0-9_ ]*$", value):
                return {'error': {'status': 400, 'message': f'Invalid value: {value} for parameter: {param}'}}
        processed_params[param] = values[0] if values else None #get first value if exists (single value for each param)

    for param in exception_params:
        value = request_args.get(param)
        if value:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return {'error': {'status': 400, 'message': f'Invalid date format: {value}. Expected YYYY-MM-DD'}}
        processed_params[param] = value

    return processed_params

def preprocess_query(search_query):
    query_tokenizer = QueryTokenizer()
    qt1, qt2, operator = query_tokenizer.tokenize(search_query) #ignore operator for now
    print(f'query_terms: {qt1}, {qt2}, {operator}')
    return qt1, qt2, operator

#get first 50 words of article
def get_document_snippet(article):
    article_words = article.split()
    if len(article_words) > 50:
        snippet = ' '.join(article_words[:50]) + '...'
    else:
        snippet = ' '.join(article_words)
    return snippet

#for applying functions to some data (eg get snippet of article)
def format_results(results_df):
    results_df = results_df.fillna('')
    results_df['article'] = results_df['article'].apply(get_document_snippet)
    return results_df
    
def get_filter_options(results):
    flat_authors = [author for sublist in results['author_names'].tolist() for author in sublist]
    unique_authors = pd.Series(flat_authors).unique().tolist()
    
    #get the unique values for each category
    filter_options = {
        'authors': [author for author in unique_authors if author != ""],
        'publications': [publication for publication in results['publication_name'].unique().tolist() if publication != ""],
        'sections': [section for section in results['section_name'].unique().tolist() if section != ""]
    }
    return filter_options

@app.route('/')
def index():
    return "This is the Sentinews API.."

@app.route('/unique_publications')
def get_unique_publications():
    start_time = time.time()
    publications = db.get_publications()
    end_time = time.time()
    retrieval_time = end_time - start_time
    return jsonify({
        'status': 200,
        'retrieval_time': retrieval_time,
        'unique_publications': publications
        })

@app.route('/articles_by_date')
def get_articles_by_date():
    # expect a date
    date = request.args.get('date')
    if not date:
        return jsonify({'status': 400, 'message': "Expected date"}), 400
    
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'status': 400, 'message': "Invalid date format. Expected YYYY-MM-DD"}), 400
        
    start_time = time.time()
    results_df = db.get_articles(start_date=date, end_date=date, limit=100)
    if results_df.empty:
        return jsonify({'status': 404, 'message': "No articles found"}), 404
    
    results_df = format_results(results_df)
    end_time = time.time()
    retrieval_time = end_time - start_time
    return jsonify({
        'status': 200,
        'retrieval_time': retrieval_time,
        'articles' : results_df.to_dict('records')
        })

@app.route('/get_saved_articles')
def get_saved_articles():
    # Expect a list of article ids
    article_ids_string = request.args.get('article_ids')  # Get the parameter as a string
    if article_ids_string:
        article_ids = [int(id) for id in article_ids_string.strip('[]').split(',')]  # Convert to list of integers
    else:
        return jsonify({'status': 400, 'message': "Expected article_ids"}), 400
    
    start_time = time.time()
    results_df = db.get_articles(article_ids=article_ids)
    if results_df.empty:
        return jsonify({'status': 404, 'message': "No articles found"}), 404

    results_df = format_results(results_df)
    end_time = time.time()
    retrieval_time = end_time - start_time
    return jsonify({
        'status': 200,
        'retrieval_time': retrieval_time,
        'saved_articles' : results_df.to_dict('records')
        })

#get results based on search query
@app.route('/search', methods=['GET'])
def get_results():
    start_time = time.time()  #start timing query search time 

    # Retrieve the arguments for each parameter 
    processed_params = process_params(request.args)
    if 'error' in processed_params:
        return jsonify(processed_params['error']), processed_params['error']['status']
    
    if processed_params == None: #if any of the parameters are invalid
        return jsonify({'status': 400, 'message': "Invalid value for parameters"}), 400
    if processed_params['type'] == None:
        return jsonify({'status': 400, 'message': "Type parameter is required"}), 400
    if processed_params['query'] == None:
        return jsonify({'status': 400, 'message': "Query parameter is required"}), 400

    #get search query and convert to lowercase
    search_query = processed_params['query'].lower()
    qt1, qt2, op = preprocess_query(search_query)

    r = Retrieval(index_filename='tools/index_tfidf.pkl')
    r_old = TFIDFScoring(index_filename='tools/index.txt')

    #identify the type of search 
    #notes: paging not implemented yet as index is too small
    results = []
    search_type = processed_params['type']
    if search_type == "phrase":
        terms = qt1 + qt2
        results = list(r.__phrase_search(terms))
        print(f'phrase search results: {results}')
    elif search_type == "boolean":
        results = r.bool_search(qt1, qt2, op)
        print(f'boolean search results: {results}')
    elif search_type == "proximity":
        return jsonify({'status': 400, 'message': "Proximity search not implemented yet"}), 400
    elif search_type == "freeform":
        terms = qt1 + qt2
        results = r_old.score(terms, k=100) #using old retrieval as new retrieval not fully updated
        results = [result[0] for result in results]
        print(f'freeform search results: {results}')
    elif search_type == "publication":
        return jsonify({'status': 400, 'message': "Publication search not implemented yet"}), 400
    else:
        return jsonify({'status': 400, 'message': "Invalid search type"}), 400

    if not results:
        return jsonify({'status': 404, 'message': "No docids found for that query in index"}), 404
    
    results_df = db.get_articles(article_ids=results)

    if results_df.empty:
        return jsonify({'status': 404, 'message': "No articles found for docid"}), 404
    else:
        results_df = format_results(results_df)

    if processed_params['request'] == None or processed_params['request'] == "all":
        filter_options = get_filter_options(results_df)

    #check if we need to convert to datetime
    if (processed_params['from'] != None and processed_params['to'] != None) or processed_params['sortBy'] == "ascendingdate" or processed_params['sortBy'] == "descendingdate":
        results_df['upload_date'] = pd.to_datetime(results_df['upload_date'])

    #if no sortBy in params assume relevance by default
    if processed_params['sortBy'] == None or processed_params['sortBy'] == "relevance":
        results_df = results_df #i think this is already done in TFIDFScoring..?
    elif processed_params['sortBy'] == "ascendingdate":
        results_df = results_df.sort_values(by='upload_date', ascending=True)
    elif processed_params['sortBy'] == "descendingdate":
        results_df = results_df.sort_values(by='upload_date', ascending=False)

    if processed_params['from'] != None and processed_params['to'] != None: 
        try:
            from_date = datetime.strptime(processed_params['from'], '%Y-%m-%d')
            to_date = datetime.strptime(processed_params['to'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'status': 400, 'message': "Invalid date format. Expected YYYY-MM-DD"}), 400
        
        results_df = results_df[(results_df['upload_date'] >= from_date) & (results_df['upload_date'] <= to_date)]

    end_time = time.time()  #end timing
    retrieval_time = end_time - start_time  #to calculate retrieval time

    #prepare response
    response = {
        'status': 200,
        'retrieval_time': retrieval_time,
        'total_results': len(results_df),
        'results': results_df.to_dict('records')
    }
    if 'filter_options' in locals(): #only include filter options if they exist (ie if request is all or not specified)
        response['filter_options'] = filter_options

    return jsonify(response), 200

if __name__ == '__main__':
    app.run()
