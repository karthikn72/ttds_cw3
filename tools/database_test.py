import database

if __name__ == "__main__":
    db = database.Database()
    # print(db.num_random_articles())
    # print(db.num_articles())
    # print(db.get_articles())
    # print(db.get_author_names([111185, 166245]))
    db.reset_index()
    db.build_index({
        'yeet1':{
            3:{'positions':[0,5,12]}, 
            7:{'positions':[3,57]}
            }, 
        'yeet2':{
            9:{'positions':[46,856,57]}, 
            2:{'positions':[23,452]}
            }
        })
    print("Database test completed successfully")
