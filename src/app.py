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
CORS(app, origins=["http://localhost:3000"])

# Load data
dataset_file = 'data/all-the-news-2-1.csv'
first_1k_docs = im.firstThousand(dataset_file)

#get first 50 words of article
def get_document_snippet(article):
    article_words = article.split()
    if len(article_words) > 50:
        snippet = ' '.join(article_words[:50]) + '...'
    else:
        snippet = ' '.join(article_words)
    return snippet

def get_document_info(docid):
    doc = first_1k_docs.iloc[docid]
    title = doc['title']
    snippet = get_document_snippet(doc['article']) 
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
    
def get_filter_options(results):
    #find earliest and oldest articles
    results['date'] = pd.to_datetime(results['date'])
    earliestArticleDate = results['date'].min()
    latestArticleDate = results['date'].max()

    #get the unique values for each category
    filter_options = {
        'authors': results['author'].unique().tolist(),
        'publications': results['publication'].unique().tolist(),
        'sections': results['section'].unique().tolist(),
        'earliestArticleDate': earliestArticleDate,
        'latestArticleDate': latestArticleDate
    }
    return filter_options

#get results based on search query
@app.route('/search', methods=['GET'])
def get_results():
    start_time = time.time()  #start timing query search time 
    search_query = request.args.get('query', '') # Get query from request

    if not search_query:
        return jsonify({'status': 400, 'message': "No search query provided"}), 400

    #tokenize query
    qtokenizer = QueryTokenizer()
    query_tokens = qtokenizer.tokenize(search_query)

    #use score function to get docids
    r = TFIDFScoring(index_filename='tools/index.txt')
    results = []

    try:
        scores = r.score(query_tokens)
        docids = [score[0] for score in scores]

        #get results
        for docid in docids:
            title, snippet, author, url, section, date, publication = get_document_info(docid)
            results.append(format_result(docid, title, snippet, author, url, section, date, publication))
        
        results_df = pd.DataFrame(results)
        results_df = results_df.fillna('')
        filter_options = get_filter_options(results_df)

    except KeyError:
        return jsonify({'status': 404, 'message': "The term does not exist in the index."}), 404

    end_time = time.time()  #end timing
    retrieval_time = end_time - start_time  #to calculate retrieval time

    #prepare response
    response = {
        'status': 200,
        'retrieval_time': retrieval_time,
        'total_results': len(results),
        'filter_options':filter_options,
        'results': results_df.to_dict('records')
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run()
