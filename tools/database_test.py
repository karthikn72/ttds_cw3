import database

if __name__ == "__main__":
    db = database.Database()
    db.create_article_table()
    print(db.get_tables())
    db.insert_article(1, 5, 'The Fox', 'Once upon on a time, far far away there lived a sly fox.', 'www.google.com', 6)
    print(db.get_tables())
    print("Database test completed successfully")
