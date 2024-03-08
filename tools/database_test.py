import database
import random
from datetime import datetime
from indexer import Indexer
import pandas as pd

if __name__ == "__main__":
    db = database.Database()

    # # Using all arguments when getting articles
    # res = db.get_articles(article_ids=[12, 19, 21, 36, 43, 46, 66, 75, 79, 87],  
    #                     start_date=datetime(2016, 1, 1), 
    #                     end_date=datetime(2019, 3, 28),
    #                     sections=['Sports News'],
    #                     publications=['TechCrunch', 'Reuters'])
    # print(res)

    # # Retrieving 10,000 random articles
    # res = db.get_articles(article_ids=random.sample(range(10 ** 6), 10000))
    # print(res)

    # # Retrieve publication_names
    # res = db.get_publications()
    # print(res)

    # senti_df = pd.DataFrame({
    #     'article_id': [1, 2, 3],
    #     'positive': [0.5, 0.7, 0.4],
    #     'negative': [0.5, 0.3, 0.6],
    #     'neutral' : [0.0, 0.2, 0.7]
    # })
    # db.update_sentiments(senti_df)

    # section_df = pd.DataFrame({
    #     'article_id': [7, 9],
    #     'section': ['Fintech', 'Fintech']
    # })
    # db.update_sections(section_df)
    # time_now = datetime(2024, 3, 5)
    # test_article = pd.DataFrame({
    #     'author': ['Jane Wilkinson', 'Dan Burn'],
    #     'title' : ['Test title 1', 'Title test 2'],
    #     'article' : ['A fireman has fallen in Lego city!', 'Yeetus deletus'],
    #     'url' : ['google.com', 'bing.com'],
    #     'section' : [None, 'World News'],
    #     'publication': ['CNN', 'BBC']
    # })

    # db.add_articles(test_article)
    # print(db.get_articles(start_date=time_now, sort_by_date='desc'))
    # print(db.get_index_by_words(['middl', 'east']))

    # # Old DB indexing
    # db.reset_index()
    # db.build_index({
    #     'yeet1':{
    #         3:{'positions':[0,5,12]}, 
    #         7:{'positions':[3,57]}
    #         }, 
    #     'yeet2':{
    #         9:{'positions':[46,856,57]}, 
    #         2:{'positions':[23,452]}
    #         }
    #     })

    # # DB Indexing
    # index_dict = {
    #     'word':['yeet1', 'yeet1', 'yeet2', 'yeet2'],
    #     'article_id': [3,7,9,2],
    #     'positions': [[0,5,12], [3,57], [46,856,57], [23,452]]
    # }
    # index_dict = pd.DataFrame(index_dict)

    # db.reset_index()
    # db.build_index(index=index_dict)
    test_articles = db.get_articles(article_ids=[6083, 4047]) 
    print(test_articles[['title', 'article']])
    id = Indexer()
    id.set_up_stopwords("tools/resources/ttds_2023_english_stop_words.txt")
    id.indexing(0, test_articles)
    article_index = id.get_index()
    print(article_index)
    print("Database test completed successfully")
