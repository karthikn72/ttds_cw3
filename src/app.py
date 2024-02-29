import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import time

# #this is to access tools folder outside of src where this app.py is located:
# import os
# import sys
# # Get the absolute path of the directory containing this script
# script_dir = os.path.dirname(os.path.abspath(__file__))
# # Get the absolute path of the parent directory
# parent_dir = os.path.dirname(script_dir)
# # Add the parent directory to the system path
# sys.path.insert(0, parent_dir)

from tools.tokenizer import Tokenizer, QueryTokenizer
from tools.retrieval import TFIDFScoring
from tools.retrieval_2 import Retrieval
from tools.database import Database

app = Flask(__name__)
CORS(app, origins=["https://sentinews-413116.nw.r.appspot.com/"])

# Load database
# dataset_file = 'data/first-1000-rows.csv'
# first_1k_docs = pd.read_csv('data/first-1000-rows.csv')
db = Database()

def process_params(request_args):
    multi_params = ["sentiment", "author", "publication", "category"]
    single_params = ["q", "from", "to", "sortBy"]

    processed_params = {}

    for param in multi_params:
        values = sorted(request_args.getlist(param))
        for value in values:
            if value == "" or not re.match("^[a-zA-Z0-9_ ]*$", value):
                return jsonify({'status': 400, 'message': f"Invalid value for parameter {param}: {value}"}), 400
        processed_params[param] = values

    for param in single_params:
        values = request_args.getlist(param)
        for value in values:
            if value == "" or not re.match("^[a-zA-Z0-9_ ]*$", value):
                return jsonify({'status': 400, 'message': f"Invalid value for parameter {param}: {value}"}), 400
        processed_params[param] = values[0] if values else None

    return processed_params

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
    flat_authors = [author for sublist in results['author_ids'].tolist() for author in sublist]
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

#get results based on search query
@app.route('/search', methods=['GET'])
def get_results():
    start_time = time.time()  #start timing query search time 

    multi_params = ["sentiment", "author", "publication", "category"]
    single_params = ["q", "from", "to", "sortBy"]

    # Initialize dictionaries to store the parameters
    multi_params = {param: [] for param in multi_params}
    single_params = {param: None for param in single_params}

    # Retrieve the arguments for each parameter and check if they are not empty and alphanumeric
    processed_params = process_params(request.args)
    print(processed_params)

    #get search query
    search_query = processed_params['q']

    #use score function to get docids
    # r = Retrieval(index_filename='tools/index_tfidf.pkl')
    r = TFIDFScoring('tools\index.txt')
    results = []

    #tokenize query
    query_tokenizer = QueryTokenizer()
    query_terms1, query_terms2, operator = query_tokenizer.tokenize(search_query) #ignore operator for now
    query_terms = query_terms1 + query_terms2
    print(f'query_terms: {query_terms}')

    try:
        # scores = r.ranked_retrieval(query_terms)
        scores = r.score(query_terms)
        docids = [score[0] for score in scores]

        print(f'docids: {docids}')

        #get results
        # for docid in docids:
        #     title, snippet, author, url, section, date, publication = get_document_info(docid)
        #     results.append(format_result(docid, title, snippet, author, url, section, date, publication))
        
        #get results from database
        results_df = db.get_articles(article_ids=docids)
        print(f'results_df: {results_df}')

        #format results df to get snippet and replace nan values
        results_df = format_results(results_df)
        
        filter_options = get_filter_options(results_df)

    except KeyError:
        return jsonify({'status': 404, 'message': "The term does not exist in the index."}), 404

    end_time = time.time()  #end timing
    retrieval_time = end_time - start_time  #to calculate retrieval time

    #prepare response
    response = {
        'status': 200,
        'retrieval_time': retrieval_time,
        'total_results': len(results_df),
        'filter_options':filter_options,
        'results': results_df.to_dict('records')
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run()
