import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import time
import threading
from datetime import datetime, timedelta
import os

from tools.tokenizer import QueryTokenizer
from tools.retrieval_2 import Retrieval
from tools.database import Database

app = Flask(__name__)
CORS(app, origins=["https://sentinews-413116.nw.r.appspot.com/", "http://localhost:3000"])

# Load database
db = Database()

#process parameters
def process_params(request_args):
    required_params = ["type", "q", "page", "request"]
    multi_params = ["sentiment", "author", "publication", "category"]
    date_params = ["from", "to"] #these are date params

    processed_params = {}

    #make sure required params are present and valid
    for param in required_params:
        value = request_args.get(param)
        if value == None:
            return {'error': {'status': 400, 'message': f"{param} parameter is required"}}
        elif value == "" or not re.match(r'^[a-zA-Z0-9_()," ]*$', value):
            return {'error': {'status': 400, 'message': f'Invalid value: {value} for required parameter: {param}'}}
        processed_params[param] = value.lower()

    #check if type is valid
    if processed_params['type'] not in ['phrase', 'boolean', 'proximity', 'freeform', 'publication']:
        return {'error': {'status': 400, 'message': f"Invalid value for type parameter"}}
    
    #define some reusable regex
    s = r'^\(\s*'
    q_req = r'"'
    word = r'[a-zA-Z0-9_]+'
    words = r'[a-zA-Z0-9_ ]+'
    word_or_phrase = r'("[a-zA-Z0-9_ ]+"|[a-zA-Z0-9_]+)'
    comma = r'\s*,\s*'
    digits = r'[0-9]+'
    boolean_operator = r'(AND|OR)'
    e = r'\s*\)$'

    #check if the query is for each type of search is valid
    if processed_params['type'] == 'proximity':
        regex = s+word_or_phrase+comma+word_or_phrase+comma+digits+e
        if not re.fullmatch(regex, processed_params['q']):
            return {'error': {'status': 400, 'message': f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}"}}
    elif processed_params['type'] == 'boolean':
        regex = s+word_or_phrase+comma+boolean_operator+comma+word_or_phrase+e
        if not re.fullmatch(regex, processed_params['q']):
            return {'error': {'status': 400, 'message': f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}"}}
    elif processed_params['type'] == 'phrase':
        regex = q_req+words+q_req
        if not re.fullmatch(regex, processed_params['q']):
            return {'error': {'status': 400, 'message': f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}"}}
    else: #general case
        if value == "" or not re.match(r'^[a-zA-Z0-9_ "]*$', value):
            return {'error': {'status': 400, 'message': f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}"}}

    #check if page is valid
    if not processed_params['page'].isdigit():
        return {'error': {'status': 400, 'message': f"Invalid value for page parameter"}}

    #check if request is valid
    if processed_params['request'] not in ['articles', 'meta']:
        return {'error': {'status': 400, 'message': f"Invalid value for request parameter"}}

    #check if there is a sortBy, if not set sortBy to None
    if 'sortBy' in request_args:
        processed_params['sortBy'] = request_args.get('sortBy').lower()
        if processed_params['sortBy'] not in ['relevance', 'ascendingdate', 'descendingdate']:
            return {'error': {'status': 400, 'message': f"Invalid value for sortBy parameter"}}
    else:
        processed_params['sortBy'] = None

    # Retrieve the arguments for each parameter and check if they are not empty and alphanumeric
    for param in multi_params:
        values = request_args.getlist(param)
        processed_values = []
        for value in values:
            if ',' in value:
                split_values = value.split(',')
                for split_value in split_values:
                    if split_value == "" or not re.match("^[a-zA-Z0-9_ ]*$", split_value):
                        return {'error': {'status': 400, 'message': f'Invalid value: {split_value} for parameter: {param}'}}
                    processed_values.append(split_value.lower())
            else:
                if value == "" or not re.match("^[a-zA-Z0-9_ ]*$", value):
                    return {'error': {'status': 400, 'message': f'Invalid value: {value} for parameter: {param}'}}
                processed_values.append(value.lower())
        processed_params[param] = processed_values

    for param in date_params:
        value = request_args.get(param)
        if value:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return {'error': {'status': 400, 'message': f'Invalid date format: {value}. Expected YYYY-MM-DD'}}
        processed_params[param] = value

    return processed_params

#get first 50 words of article
def get_document_snippet(article):
    article_words = article.split()
    if len(article_words) > 48:
        snippet = ' '.join(article_words[:48]) + '...'
    else:
        snippet = ' '.join(article_words)
    return snippet

#to replace nulls in lists
def replace_nulls(value):
    if isinstance(value, list):
        return ["" if v is None else v for v in value]
    else:
        return value

#for applying functions to some data (eg get snippet of article)
def format_results(results_df):
    results_df = results_df.fillna('')
    results_df = results_df.applymap(replace_nulls)
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
    publications = db.get_publications()
    return jsonify({
        'status': 200,
        'unique_publications': publications
        })

@app.route('/get_live')
def get_live():  
    #get type parameter
    type = request.args.get('type')
    if type == None:
        return jsonify({'status': 400, 'message': "Expected type parameter"}), 400
    elif type.lower() not in ['digest', 'trending']:
        return jsonify({'status': 400, 'message': "Invalid value for type parameter"}), 400
    
    start_time = time.time()
    if type.lower() == 'digest':
        #set date internally to be current day, for now use hardcoded date that returns results
        hardcoded_date = "2018-03-05"
        date = datetime.strptime(hardcoded_date, "%Y-%m-%d")
        results_df = db.get_articles(start_date=date, end_date=date, limit=100)

    elif type.lower() == 'trending':
        return jsonify({'status': 400, 'message': "trending not implemented yet"}), 400

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
    results_df = db.get_articles(article_ids=article_ids, limit=100)

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
    
    print(f"Processed params: {processed_params}")
    
    #get search query
    search_query = processed_params['q']
    
    #initialize tokenizer and retrieval
    q = QueryTokenizer()
    r = Retrieval(index_filename='tools/index_tfidf.pkl')

    #identify the type of search 
    search_type = processed_params['type']
    if search_type == "phrase":
        try:
            terms = q.tokenize_free_form(search_query)
        except Exception as e:
            return jsonify({'status': 500, 'message': "Error during tokenization"}), 500
        try:
            results = r.free_form_retrieval(terms)
        except KeyError as e:
            return jsonify({'status': 404, 'message': "Could not find term in index"}), 404
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        results = [x[0] for x in results]

    elif search_type == "boolean":
        parts = search_query.strip("()").split(",")
        t1, op, t2 = [part.strip() for part in parts]
        formatted = f"{t1} {op} {t2}"
        try:
            t1, t2, op = q.tokenize_bool(formatted)
        except Exception as e:
            return jsonify({'status': 500, 'message': "Error during tokenization"}), 500
        try:
            results = r.bool_retrieval(t1, t2, op)
        except KeyError as e:
            return jsonify({'status': 404, 'message': "Could not find term in index"}), 404
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        results = [x[0] for x in results]

    elif search_type == "proximity":
        parts = search_query.strip("()").split(",")
        t1, t2, k = [part.strip() for part in parts]
        print(t1, t2, k)
        try:
            t1 = q.process_word(t1)
            t2 = q.process_word(t2)
        except Exception as e:
            print(e)
            return jsonify({'status': 500, 'message': "Error during tokenization"}), 500
        print(t1, t2, k)
        try:
            results = r.proximity_retrieval(t1, t2, int(k))
        except KeyError as e:
            return jsonify({'status': 404, 'message': "Could not find term in index"}), 404
        print(results)
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        results = [x[0] for x in results]

    elif search_type == "freeform":
        try:
            terms = q.tokenize_free_form(search_query)
        except Exception as e:
            return jsonify({'status': 500, 'message': "Error during tokenization"}), 500
        try:
            results = r.free_form_retrieval(terms)
        except KeyError as e:
            return jsonify({'status': 404, 'message': "Could not find term in index"}), 404
        results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        results = [x[0] for x in results]

    elif search_type == "publication":
        publications = [search_query]
        print(publications)

    else:
        return jsonify({'status': 400, 'message': "Invalid search type"}), 400

    #check for date range
    if processed_params['from'] != None and processed_params['to'] != None: 
        try:
            start_date = datetime.strptime(processed_params['from'], '%Y-%m-%d')
            end_date = datetime.strptime(processed_params['to'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'status': 400, 'message': "Invalid date format. Expected YYYY-MM-DD"}), 400
    else:
        start_date = None
        end_date = None
        
    #check for sortBy 
    sort_by_date = None
    if processed_params['sortBy'] == None or processed_params['sortBy'] == "relevance":
        sort_by_date = None
    elif processed_params['sortBy'] == "ascendingdate": #not true sort, only sorting the 100 retrieved from database
        sort_by_date = "asc"
    elif processed_params['sortBy'] == "descendingdate":
        sort_by_date = "desc"

    #apply filters if they exist
    authors = None
    sentiments = None
    categories = None
    if 'publication' in processed_params:
        publications = processed_params['publication']
    else:
        publications = None

    #get results from database
    if search_type == "publication":
        offset = int(processed_params['page'])*100
        results_df = db.get_articles(publications=publications, start_date=start_date, end_date=end_date, sort_by_date=sort_by_date, limit=100, offset=offset)
    else:
        print("running normal search")
        results_current_page = results[int(processed_params['page'])*100:int(processed_params['page'])*100+100]
        print(results_current_page)
        print(publications, start_date, end_date, sort_by_date)
        results_df = db.get_articles(article_ids=results_current_page, publications=publications, start_date=start_date, end_date=end_date, sort_by_date=sort_by_date, limit=100)

    if results_df.empty:
        return jsonify({'status': 404, 'message': "No articles found for docid"}), 404
    else:
        results_df = format_results(results_df)

    if processed_params['request'] == None or processed_params['request'] == "meta":
        filter_options = get_filter_options(results_df)

    end_time = time.time()  #end timing
    retrieval_time = end_time - start_time  #to calculate retrieval time

    #prepare response
    response = {
        'status': 200,
        'retrieval_time': retrieval_time,
        'total_results': len(results),
        'results': results_df.to_dict('records')
    }
    if 'filter_options' in locals(): #only include filter options if they exist (ie if request is all or not specified)
        response['filter_options'] = filter_options

    return jsonify(response), 200

if __name__ == '__main__':
    app.run()
