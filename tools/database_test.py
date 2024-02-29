import database
import random
import pandas as pd

if __name__ == "__main__":
    db = database.Database()
    # print(db.num_random_articles())
    # print(db.num_articles())
    res = db.get_articles()
    # print(res.author_names)
    # print(res.iloc[0].author_names[0].type())
    # print(db.get_author_names([111185, 166245]))
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
    index_dict = {
        'word':['yeet1', 'yeet1', 'yeet2', 'yeet2'],
        'article_id': [3,7,9,2],
        'positions': [[0,5,12], [3,57], [46,856,57], [23,452]]
    }
    index_dict = pd.DataFrame(index_dict)

    db.reset_index()
    db.build_index(index=index_dict)
    print("Database test completed successfully")
