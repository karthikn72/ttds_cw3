import os

from google.cloud.sql.connector import Connector, IPTypes
import pg8000

import sqlalchemy as db

class Database:
    def __init__(self):
        self.engine = self.connect_with_connector()


    def connect_with_connector(self) -> db.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of Postgres.

        Uses the Cloud SQL Python Connector package.
        """

        instance_connection_name = "sentinews-413116:europe-west2:sentinews-db"
        db_user = 'postgres'
        db_pass = 'senti2024'
        db_name = 'news_db'

        ip_type = IPTypes.PUBLIC
        connector = Connector()

        def getconn() -> pg8000.dbapi.Connection:
            conn: pg8000.dbapi.Connection = connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db=db_name,
                ip_type=ip_type,
            )
            return conn

        engine = db.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
        )
        print("Connected to database successfully")
        return engine 

    def create_article_table(self):
        with self.engine.connect() as db_conn:
            metadata = db.MetaData()
            articles = db.Table('articles', metadata,
                        db.Column('article_id', db.Integer(),primary_key=True),
                        db.Column('author_id', db.String(255), nullable=True),
                        db.Column('title', db.String(500), nullable=False),
                        db.Column('article', db.String(), nullable=False),
                        db.Column('url', db.String(), nullable=True),
                        db.Column('publication_id', db.String(), nullable=False)
                        )

            metadata.create_all(db_conn)
            db_conn.commit()

            query = db.insert(Articles).values(Id=1, Author='John', Title='The Great Escape', Article='Yeetus feetus lorem ipsum', URL='yeet', Section='Sports', Publication='Guardian')
            result = db_conn.execute(query)
            output = db_conn.execute(Articles.select()).fetchall()
            print(output)
            print(metadata.tables.keys())

    def get_tables(self):
        return self.engine.table_names()
    
    def insert_article(self, article_id, author_id, title, article, url, publication_id):
        with self.engine.connect() as db_conn:
            metadata = db.MetaData(bind=db_conn)

