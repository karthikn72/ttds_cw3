import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import time
from threading import Thread
from datetime import datetime, timedelta
import os
from functools import lru_cache

from tools.tokenizer import QueryTokenizer
from tools.retrieval import Retrieval
from tools.database import Database

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://sentinews-413116.web.app"}})

# Load database
db = Database()

class HandleRequestError(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status
        super().__init__(self.message)

class ParamsProcessingError(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status
        super().__init__(self.message)

class HandleRequestThread(Thread):
    def __init__(self, processed_params):
        Thread.__init__(self)
        self.processed_params = processed_params
        self.results = None
        self.error = None

    def run(self):
        try:
            self.results = handle_request(self.processed_params)
        except HandleRequestError as e:
            self.error = e
        except Exception as e:
            self.error = HandleRequestError(e, 500)

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
            raise ParamsProcessingError(f"{param} parameter is required", 400)
        elif value == "" or not re.match(r'^[a-zA-Z0-9_(),"\' .:-]*$', replace_curly_quotes(value)):
            raise ParamsProcessingError(f'Invalid value: {value} for required parameter: {param}', 400)
        processed_params[param] = replace_curly_quotes(value).lower()

    #check if type is valid
    if processed_params['type'] not in ['phrase', 'boolean', 'proximity', 'freeform', 'publication']:
        raise ParamsProcessingError(f"Invalid value for type parameter", 400)
    
    #define some reusable regex
    s = r'^\(\s*'
    q_req = r'"'
    word = r'[a-zA-Z0-9_\'.:-]+'
    words = r'[a-zA-Z0-9_\' .:-]+'
    word_or_phrase = r'("[a-zA-Z0-9_\' .:-]+"|[a-zA-Z0-9_\'.:-]+)'
    comma = r'\s*,\s*'
    valid_digit = r'[0-9]+'
    boolean_operator = r'(AND|OR|and|or)'
    e = r'\s*\)$'

    #check if the query is for each type of search is valid
    if processed_params['type'] == 'proximity':
        regex = s+word+comma+word+comma+valid_digit+e
        if not re.fullmatch(regex, processed_params['q']):
            raise ParamsProcessingError(f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}", 400)
    elif processed_params['type'] == 'boolean':
        regex = s+word_or_phrase+comma+boolean_operator+comma+word_or_phrase+e
        if not re.fullmatch(regex, processed_params['q']):
            raise ParamsProcessingError(f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}", 400)
    elif processed_params['type'] == 'phrase':
        regex = q_req+words+q_req
        if not re.fullmatch(regex, processed_params['q']):
            raise ParamsProcessingError(f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}", 400)
    elif processed_params['type'] == 'publication':
        if not processed_params['q'].startswith('publication:'):
            raise ParamsProcessingError("Invalid value: {processed_params['q']} for search type: {processed_params['type']}",400)
    else: #general case
        if value == "" or not re.match(r'^[a-zA-Z0-9_ .:-]*("[a-zA-Z0-9_ .:-]*")?[a-zA-Z0-9_ .:-]*$', value):
            raise ParamsProcessingError(f"Invalid value: {processed_params['q']} for search type: {processed_params['type']}", 400)

    #check if page is valid
    if not processed_params['page'].isdigit():
        raise ParamsProcessingError(f"Invalid value for page parameter", 400)

    #check if request is valid
    if processed_params['request'] not in ['articles', 'meta']:
        raise ParamsProcessingError(f"Invalid value for request parameter", 400)

    #check if there is a sortBy in the request args, if not set sortBy to None
    if request_args.get('sortBy') != None:
        processed_params['sortBy'] = request_args.get('sortBy').lower()
        if processed_params['sortBy'] not in ['relevance', 'ascendingdate', 'descendingdate']:
            raise ParamsProcessingError(f"Invalid value for sortBy parameter", 400)
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
                    if split_value == "" or not re.match("^[a-zA-Z0-9_\' ]*$", replace_curly_quotes(split_value)):
                        raise ParamsProcessingError(f'Invalid value: {split_value} for parameter: {param}', 400)
                    processed_values.append(replace_curly_quotes(split_value).lower())
            else:
                if value == "" or not re.match("^[a-zA-Z0-9_\' ]*$", value):
                    raise ParamsProcessingError(f'Invalid value: {value} for parameter: {param}', 400)
                processed_values.append(value.lower())
        processed_params[param] = processed_values

    for param in date_params:
        value = request_args.get(param)
        if value:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                raise ParamsProcessingError('Invalid date format: {value}. Expected YYYY-MM-DD', 400)
        processed_params[param] = value

    return processed_params

#replace curly quotes if found
def replace_curly_quotes(string):
    if '“' in string or '”' in string or '‘' in string or '’' in string:
        # Replace opening curly quotes with straight quotes
        string = re.sub(r'[“‘]', '"', string)
        # Replace closing curly quotes with straight quotes
        string = re.sub(r'[”’]', '"', string)
    return string

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

def sort_by_relevance(results_df, relevance_order, start, end):
    #remove any article ids not in results_df from relevance_order (if filters were applied)
    relevance_order = [article_id for article_id in relevance_order if article_id in results_df['article_id'].tolist()]
    # get 100 in order of relevance
    relevance_order = relevance_order[start:end]
    results_df = results_df[results_df['article_id'].isin(relevance_order)]
    results_df['article_id'] = results_df['article_id'].astype('category')
    results_df['article_id'] = results_df['article_id'].cat.set_categories(relevance_order)
    results_df = results_df.sort_values(['article_id'])
    categorical_columns = results_df.select_dtypes(['category']).columns
    results_df[categorical_columns] = results_df[categorical_columns].astype('object')
    return results_df

def convert_to_immutable(processed_params):
    immutable_params = {}
    for key, value in processed_params.items():
        if isinstance(value, list):
            immutable_params[key] = tuple(value)
        else:
            immutable_params[key] = value
    return frozenset(immutable_params.items())

@lru_cache(maxsize=500)
def process_search_query(processed_params_frozenset):
    processed_params = dict(processed_params_frozenset)

    #get search query
    search_query = processed_params['q']
    
    #initialize tokenizer and retrieval
    q = QueryTokenizer()
    r = Retrieval()

    results = []
    results_scores = []
    pubs_q = []

    #identify the type of search 
    search_type = processed_params['type']
    if search_type == "phrase":
        try:
            print(f'search_query: {search_query}')
            terms, exp_terms = q.tokenize_free_form(search_query)
        except (ValueError) as e:
            raise HandleRequestError(str(e), 404)
        except (Exception) as e:
            raise HandleRequestError("Error during tokenization", 404)
        try:
            print(f'terms: {terms}, expanded_terms: {exp_terms}')
            results = r.free_form_retrieval(terms, exp_terms)
        except (KeyError) as e:
            raise HandleRequestError("Could not find term in index", 404)
        except (Exception) as e:
            raise HandleRequestError("Error during retrieval", 404)
        results_scores = results
        results = results.keys()

    elif search_type == "boolean":
        parts = search_query.strip("()").split(",")
        t1, op, t2 = [part.strip() for part in parts]
        #convert op to something that can be used in the retrieval function
        if op.strip().lower() == "and":
            op = "AND"
        elif op.strip().lower() == "or":
            op = "OR"
        else:
            raise HandleRequestError("Invalid boolean operator", 400)
        try:
            print(f't1: {t1}, t2: {t2}, op: {op}')
            t1, exp_t1 = q.tokenize_free_form(t1)
            t2, exp_t2 = q.tokenize_free_form(t2)
        except (ValueError) as e:
            raise HandleRequestError(str(e), 404)
        except (Exception) as e:
            raise HandleRequestError("Error during tokenization", 404)
        try:
            print(f't1: {t1}, exp_t1: {exp_t1}, t2: {t2}, exp_t2: {exp_t2}, op: {op}')
            results = r.bool_retrieval(t1, exp_t1, t2, exp_t2, op)
        except (KeyError) as e:
            raise HandleRequestError("Could not find term in index", 404)
        except (Exception) as e:
            raise HandleRequestError("Error during retrieval", 404)
        results_scores = results
        results = results.keys()

    elif search_type == "proximity":
        parts = search_query.strip("()").split(",")
        t1, t2, k = [part.strip() for part in parts]
        if int(k) < 1:
            raise HandleRequestError("Invalid value for k", 400)
        try:
            print(f't1: {t1}, t2: {t2}, k: {k}')
            t1 = q.process_word(t1)
            t2 = q.process_word(t2)
        except (ValueError) as e:
            raise HandleRequestError(str(e), 404)
        except (Exception) as e:
            raise HandleRequestError("Error during tokenization", 404)
        try:
            print(f't1: {t1}, t2: {t2}, k: {k}')
            results = r.proximity_retrieval(t1, t2, int(k))
        except (KeyError) as e:
            raise HandleRequestError("Could not find term in index", 404)
        except (Exception) as e:
            raise HandleRequestError("Error during retrieval", 404)
        results_scores = results
        results = results.keys()

    elif search_type == "freeform":
        try:
            print(f'search_query: {search_query}')
            terms, exp_terms = q.tokenize_free_form(search_query)
        except (ValueError) as e:
            raise HandleRequestError(str(e), 404)
        except (Exception) as e:
            raise HandleRequestError("Error during tokenization", 404)
        try:
            print(f'terms: {terms}, exp_terms: {exp_terms}')
            results = r.free_form_retrieval(terms, exp_terms)
        except (KeyError) as e:
            raise HandleRequestError("Could not find term in index", 404)
        except (Exception) as e:
            raise HandleRequestError("Error during retrieval", 404)
        results_scores = results
        results = results.keys()

    elif search_type == "publication":
        search_query = search_query.split(":")[1].strip()
        existing_pubs = db.get_publications()
        existing_pubs = [pub.strip().lower() for pub in existing_pubs]
        if search_query not in existing_pubs:
            raise HandleRequestError("Could not find publication", 404)
        pubs_q = [search_query]
        print(f'publications: {pubs_q}')

    else:
        raise HandleRequestError("Invalid search type", 400)
    
    return results, results_scores, pubs_q

def handle_request(processed_params):
    start_time = time.time()  #start timing query search time 

    try: 
        immutable_params = convert_to_immutable(processed_params)
        results, results_scores, publications = process_search_query(immutable_params)
    except HandleRequestError as e:
        raise e

    #check for date range
    if processed_params['from'] != None and processed_params['to'] != None: 
        try:
            start_date = datetime.strptime(processed_params['from'], '%Y-%m-%d')
            end_date = datetime.strptime(processed_params['to'], '%Y-%m-%d')
        except ValueError:
            raise HandleRequestError("Invalid date format. Expected YYYY-MM-DD", 400)
    else:
        start_date = None
        end_date = None
        
    #check for sortBy 
    sort_by_date = None
    relevance_order = []
    if processed_params['type'] == "publication":
        if processed_params['sortBy'] == None or processed_params['sortBy'] == "descendingdate":
            sort_by_date = "desc" #default for publication search
        elif processed_params['sortBy'] == "ascendingdate":
            sort_by_date = "asc"
    else:
        if processed_params['sortBy'] == None or processed_params['sortBy'] == "relevance":
            sort_by_date = None
            results_scores = sorted(results_scores.items(), key=lambda x: x[1], reverse=True)
            relevance_order = [x[0] for x in results_scores]
        elif processed_params['sortBy'] == "ascendingdate": 
            sort_by_date = "asc"
        elif processed_params['sortBy'] == "descendingdate":
            sort_by_date = "desc"  

    #apply filters if they exist
    authors = processed_params['author'] if processed_params['author'] else None
    sentiments = processed_params['sentiment'] if processed_params['sentiment'] else None
    if processed_params['type'] != "publication":
        publications = processed_params['publication'] if processed_params['publication'] else None
    sections = processed_params['category'] if processed_params['category'] else None

    #get results from database
    if processed_params['type'] == "publication":
        try:
            print(f'publications: {publications}, start_date: {start_date}, end_date: {end_date}, sort_by_date: {sort_by_date}, sections: {sections}')
            results_df = db.get_articles(publications=publications, start_date=start_date, end_date=end_date, sort_by_date=sort_by_date, sections=sections, limit=5000)
        except (Exception) as e:
            raise HandleRequestError('error fetching articles', 404)
    else:
        if results == []:
            raise HandleRequestError("Words could not be found in the index", 404)
        results_df = db.get_articles(article_ids=results, publications=publications, start_date=start_date, end_date=end_date, sort_by_date=sort_by_date, sections=sections, limit=5000)

    end_time = time.time()  #end timing
    retrieval_time = end_time - start_time  #to calculate retrieval time

    return results_df, relevance_order, retrieval_time

def process_results(processed_params, results_df, relevance_order, retrieval_time):
    if results_df.empty:
        if processed_params['publication'] or processed_params['from'] or processed_params['to'] or processed_params['category']:
            return jsonify({'status': 200, 'message': "No articles found with filter conditions"}), 200
        else:
            return jsonify({'status': 404, 'message': "No articles found for docid"}), 404
    else:
        #for now, filter with pandas in the API
        if processed_params['author']:
            authors = [author.lower() for author in processed_params['author']]
            results_df = results_df[results_df['author_names'].apply(lambda x: isinstance(x, list) and any(author in name.lower() for author in authors for name in x if name is not None))]

        if processed_params['sentiment']:
            sentiments = [sentiment.lower() for sentiment in processed_params['sentiment']]
            results_df = results_df[results_df['sentiment'].apply(lambda x: isinstance(x, str) and pd.notnull(x) and x.lower() in sentiments)]

        if results_df.empty:
            return jsonify({'status': 200, 'message': "No articles found with filter conditions"}), 200

        #to return only 100 articles depending on page number
        start = (int(processed_params['page']))*100
        end = start + 100
        if start >= len(results_df):
            return jsonify({'status': 404, 'message': "No articles found for page"}), 404
        if relevance_order:
            print(f'start: {start}, end: {end}')
            print(f'len of all results: {len(results_df)}')
            print(f'len of page results: {len(results_df[start:end])}')
            return_results_df = sort_by_relevance(results_df, relevance_order, start, end)
            return_results_df = format_results(return_results_df)
        else:
            return_results_df = format_results(results_df[start:end])

    if processed_params['request'] == None or processed_params['request'] == "meta":
        filter_options = get_filter_options(results_df)

    #prepare response
    response = {
        'status': 200,
        'retrieval_time': retrieval_time,
        'total_results': len(results_df),
        'results': return_results_df.to_dict('records')
    }
    if 'filter_options' in locals(): #only include filter options if they exist (ie if request is all or not specified)
        response['filter_options'] = filter_options

    return jsonify(response), 200

@app.route('/')
def index():
    return "This is the Sentinews API.."

#get results based on search query
@app.route('/search', methods=['GET'])
def get_results():
    # Retrieve the arguments for each parameter 
    try:
        processed_params = process_params(request.args)
    except ParamsProcessingError as e:
        return jsonify({'status': e.status, 'message': e.message}), e.status
    
    print(f"Processed params: {processed_params}")
    
    # Create a new thread for handle_request
    thread = HandleRequestThread(processed_params)
    thread.start()

    # Wait for the thread to finish
    thread.join()

    # Get the results from the thread
    if thread.error is not None:
        return jsonify({'status': thread.error.status, 'message': str(thread.error)}), thread.error.status

    if thread.results is not None:
        results_df, relevance_order, retrieval_time = thread.results
        return process_results(processed_params, results_df, relevance_order, retrieval_time)
    else:
        return jsonify({'status': 500, 'message': "An error occurred"}), 500
    
@app.route('/unique_publications')
def get_unique_publications():
    publications = db.get_publications()
    return jsonify({
        'status': 200,
        'unique_publications': publications
        })

def get_digest(current_date):
    results_df = db.get_articles(start_date=current_date, end_date=current_date, limit=100)
    return results_df

def get_trending(current_date):
    results_df = db.get_articles(start_date=current_date, end_date=current_date, limit=200)
    if not results_df.empty:
        results_df = results_df.sample(n=5)
    return results_df

@app.route('/get_live')
def get_live():  
    #get type parameter
    type = request.args.get('type')
    if type == None:
        return jsonify({'status': 400, 'message': "Expected type parameter"}), 400
    elif type.lower() not in ['digest', 'trending']:
        return jsonify({'status': 400, 'message': "Invalid value for type parameter"}), 400
    
    start_time = time.time()
    # current_date = datetime.now()
    # for now use hardcoded date
    current_date = datetime(2018, 6, 1)

    if type.lower() == 'digest':
        results_df = get_digest(current_date)

    elif type.lower() == 'trending':
        results_df = get_trending(current_date)

    if results_df.empty:
        current_date = (datetime.now() - timedelta(days=1))
        if type.lower() == 'digest':
            results_df = get_digest(current_date)
        elif type.lower() == 'trending':
            results_df = get_trending(current_date)

    if results_df.empty:
        return jsonify({'status': 404, 'message': "No articles found"}), 404
    
    results_df = format_results(results_df)
    
    end_time = time.time()
    retrieval_time = end_time - start_time

    if type.lower() == 'digest':
        return jsonify({
            'status': 200,
            'retrieval_time': retrieval_time,
            'digest' : results_df.to_dict('records'),
            'date': current_date
            })
    elif type.lower() == 'trending':
        #just return id and title
        return jsonify({
            'status': 200,
            'trending' : results_df[['article_id', 'title']].to_dict('records'),
            'date': current_date
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

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))
