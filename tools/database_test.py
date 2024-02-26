import database

if __name__ == "__main__":
    db = database.Database()
    print(db.get_articles())
    print(db.get_author_names([111185, 166245]))
    # print(db.build_index({
    #     'yeet1':{
    #         3:{'positions':[0,5,12], 'tfidf':65}, 
    #         7:{'positions':[3,57], 'tfidf':36}
    #         }, 
    #     'yeet2':{
    #         9:{'positions':[46,856,57], 'tfidf':73}, 
    #         2:{'positions':[23,452], 'tfidf':657}
    #         }
    #     }))
    # print(db.doc_frequency('yeet1'))
    # print(db.term_frequency(word_id=1, article_id=3))
    print("Database test completed successfully")
