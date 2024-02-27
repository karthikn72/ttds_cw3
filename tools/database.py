import os
import timer
import random
import pandas as pd
from tqdm import tqdm

import sqlalchemy as db
from sqlalchemy.dialects.postgresql import insert

from google.cloud.sql.connector import Connector, IPTypes
import pg8000

import warnings
warnings.filterwarnings(action='ignore')

class Database:
    def __init__(self):
        self.engine = self.connect_with_connector()
        self.metadata = db.MetaData()

    def connect_with_connector(self) -> db.engine.base.Engine:
        """
        Initializes a connection pool for a Cloud SQL instance of Postgres.
        Uses the Cloud SQL Python Connector package.
        """
        instance_connection_name = "sentinews-413116:us-central1:sentinews-db"
        db_user = 'postgres'
        db_pass = 'senti2024'
        db_name = 'sentinews'

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
        db_timer = timer.Timer("Connected to database in {:.4f}s")
        db_timer.start()
        engine = db.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
        )
        db_timer.stop()
        return engine 

    def get_tables(self):
        t = timer.Timer("Got tables in {:.4f}s")
        with self.engine.connect() as db_conn:
            t.start()
            tables = db.inspect(db_conn).get_table_names()
            t.stop()
            return tables
    
    def doc_frequency(self, word):
        with self.engine.connect() as db_conn:
            if word is int:
                query = db.text(f'SELECT COUNT(word_id) FROM index_table WHERE word_id = :word') 
            else:
                query = db.text(f'SELECT COUNT(index_table.word_id) FROM index_table, words WHERE index_table.word_id = words.word_id and words.word = :word')
            t = timer.Timer("Got df in {:.4f}s")
            t.start()
            result = db_conn.execute(query, {'word':word}).fetchone()
            t.stop()
            if result:
                return result[0]
            else:
                return 0

    def term_frequency(self, word_id, article_id):
        with self.engine.connect() as db_conn:
            query = db.text(f'SELECT CARDINALITY(positions) FROM index_table WHERE word_id = :word_id and article_id = :article_id')
            t = timer.Timer("Got tf in {:.4f}s")
            t.start()
            result = db_conn.execute(query, {'word_id':word_id, 'article_id':article_id}).fetchone()
            t.stop()
            if result:
                return result[0]
            else:
                return 0
            
    def num_articles(self):
        conn_t = timer.Timer("Connected in {:.4f}s")
        conn_t.start()
        with self.engine.connect() as db_conn:
            conn_t.stop()
            query = db.text(f'SELECT COUNT(*) FROM articles')
            t = timer.Timer("Got count in {:.4f}s")
            t.start()
            result = db_conn.execute(query).fetchone()
            t.stop()
            if result:
                return result[0]
            else:
                return 0

    def num_random_articles(self):
        conn_t = timer.Timer("Connected in {:.4f}s")
        t = timer.Timer("Got count in {:.4f}s")
        ls = random.sample(range(10**6), 10000)
        t.start()
        for val in tqdm(ls):
            with self.engine.connect() as db_conn:
                query = db.text(f'SELECT COUNT(*) FROM articles where article_id = {val}')
                result = db_conn.execute(query).fetchone()
        t.stop()
    
    def get_articles(self,
                     article_ids: list[int] = None,
                     limit=10,
                     offset=0,
                     ):
        with self.engine.connect() as db_conn:
            if article_ids:
                query = db.text(f'SELECT article_id, upload_date, author_ids, title, article, url, sections.section_name, publications.publication_name \
                                    FROM articles, sections, publications \
                                    WHERE article_id IN {tuple(article_ids)} AND sections.section_id = articles.section_id AND publications.publication_id = articles.publication_id\
                                    LIMIT {limit} OFFSET {offset}')
            else:
                query = db.text(f'SELECT article_id, upload_date, author_ids, title, article, url, sections.section_name, publications.publication_name \
                                    FROM articles, sections, publications \
                                    WHERE sections.section_id = articles.section_id AND publications.publication_id = articles.publication_id\
                                    LIMIT {limit} OFFSET {offset}')
            t = timer.Timer("Got results in {:.4f}s")
            t.start()
            article_df = pd.read_sql(query, db_conn)
            print(article_df.columns)
            t.stop()
            return article_df

    def get_author_names(self, author_ids):
        with self.engine.connect() as db_conn:
            query = db.text(f'SELECT * FROM authors WHERE author_id IN {tuple(author_ids)}')
            t = timer.Timer("Got author_names in {:.4f}s")
            t.start()
            author_df = pd.read_sql(query, db_conn)
            t.stop()
            return author_df

    def add_words(self, words, conn):
        self.words = db.Table('words', self.metadata, autoload_with=self.engine)
        query = insert(self.words).values(words).on_conflict_do_nothing().returning(self.words.c.word_id)
        t = timer.Timer('Inserted words in {:.4f}s')
        t.start()
        conn.execute(query)
        t.stop()

    def add_index(self, index, conn):
        insert_statement = db.text("""
            INSERT INTO index_table (word_id, article_id, positions)
            SELECT words.word_id, :article_id, :positions
            FROM words
            WHERE words.word = :word
            ON CONFLICT (word_id,article_id) DO UPDATE SET positions = EXCLUDED.positions
        """)
        t = timer.Timer('Built index in {:.4f}s')
        t.start()
        for word in index:
            for article_id in index[word]:
                args = {
                    'word':word,
                    'article_id':article_id,
                    'positions':index[word][article_id]['positions'],
                    }
                conn.execute(
                    insert_statement,
                    args
                )
        t.stop()

    def calc_tfidf(self, conn):
        sql_path = "tools/databases/calc_tfidf.sql"
        with open(sql_path) as file:
            query = db.text(file.read())
            conn.execute(query)

    def build_index(self, index):
        with self.engine.connect() as db_conn:
            try:
                words = [{'word':word} for word in index]
                self.add_words(words=words, conn=db_conn)
                self.add_index(index=index, conn=db_conn)
                self.calc_tfidf(conn=db_conn)
                db_conn.commit()
                return "Index build successful"
            except Exception as e:
                db_conn.rollback()
                raise e

    def get_index_by_words(self, words: list[str]):
        conn_t = timer.Timer("Connected in {:.4f}s")
        conn_t.start()
        with self.engine.connect() as db_conn:
            conn_t.stop()
            query = f"SELECT * FROM index_table WHERE word_id = (SELECT word_id FROM words WHERE word in {tuple(words)})"
            t = timer.Timer("Got index in {:.4f}s")
            t.start()
            index_df = pd.read_sql(query, db_conn)
            t.stop()
            return index_df

    def index_length(self):
        conn_t = timer.Timer("Connected in {:.4f}s")
        conn_t.start()
        with self.engine.connect() as db_conn:
            conn_t.stop()
            query = db.text(f'SELECT COUNT(*) FROM index_table')
            t = timer.Timer("Got length in {:.4f}s")
            t.start()
            result = db_conn.execute(query).fetchone()
            t.stop()
            if result:
                return result[0]
            else:
                return 0

    def num_words(self):
        conn_t = timer.Timer("Connected in {:.4f}s")
        conn_t.start()
        with self.engine.connect() as db_conn:
            conn_t.stop()
            query = db.text(f'SELECT COUNT(*) FROM words')
            t = timer.Timer("Got length in {:.4f}s")
            t.start()
            result = db_conn.execute(query).fetchone()
            t.stop()
            if result:
                return result[0]
            else:
                return 0

    def reset_index(self, words=True):
        sql_paths = ["tools/databases/create_index_table.sql"]
        if words:
            sql_paths.append("tools/databases/create_word_table.sql")
        while True:
            confirm = input("Are you sure you want to reset the entire index? (y/n): ").lower()
            if confirm in ['y', 'n']:
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
        if confirm == 'y':
            with self.engine.connect() as db_conn:
                for sql_path in sql_paths:
                    with open(sql_path) as file:
                        query = db.text(file.read())
                        db_conn.execute(query)
            return "Index reset"
        return "Cancelled index reset"
