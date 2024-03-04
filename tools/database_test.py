import database
import random
from datetime import datetime
import pandas as pd

if __name__ == "__main__":
    db = database.Database()

    # Using all arguments when getting articles
    res = db.get_articles(article_ids=[12, 19, 21, 36, 43, 46, 66, 75, 79, 87],  
                        start_date=datetime(2016, 1, 1), 
                        end_date=datetime(2019, 3, 28),
                        sections=['Sports News'],
                        publications=['TechCrunch', 'Reuters'])
    print(res)

    # # Retrieving 10,000 random articles
    # res = db.get_articles(article_ids=random.sample(range(10 ** 6), 10000))
    # print(res)

    # Retrieve publication_names
    res = db.get_publications()
    print(res)

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
    print("Database test completed successfully")
