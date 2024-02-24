import os
import timer
import pandas as pd

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
                query = db.text(f'SELECT COUNT(word_id) FROM index WHERE word_id = :word') 
            else:
                query = db.text(f'SELECT COUNT(index.word_id) FROM index, words WHERE index.word_id = words.word_id and words.word = :word')
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
            query = db.text(f'SELECT CARDINALITY(positions) FROM index WHERE word_id = :word_id and article_id = :article_id')
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
    
    def build_index(self, index):
        self.words = db.Table('words', self.metadata, autoload_with=self.engine)
        with self.engine.connect() as db_conn:
            try:
                words = [{'word':word} for word in index]
                query = insert(self.words).values(words).on_conflict_do_nothing().returning(self.words.c.word_id)
                t = timer.Timer('Inserted words in {:.4f}s')
                t.start()
                db_conn.execute(query)
                t.stop()
                insert_statement = db.text("""
                    INSERT INTO index (word_id, article_id, positions, tfidf)
                    SELECT words.word_id, :article_id, :positions, :tfidf
                    FROM words
                    WHERE words.word = :word
                    ON CONFLICT (word_id,article_id) DO UPDATE SET positions = EXCLUDED.positions, tfidf = EXCLUDED.tfidf
                """)
                t = timer.Timer('Built index in {:.4f}s')
                t.start()
                for word in index:
                    for article_id in index[word]:
                        args = {
                            'word':word,
                            'article_id':article_id,
                            'positions':index[word][article_id]['positions'],
                            'tfidf':index[word][article_id]['tfidf']
                            }
                        db_conn.execute(
                            insert_statement,
                            args
                        )
                t.stop()
                db_conn.commit()
                return "Index build successful"
            except Exception as e:
                db_conn.rollback()
                raise e

    def index_length(self):
        conn_t = timer.Timer("Connected in {:.4f}s")
        conn_t.start()
        with self.engine.connect() as db_conn:
            conn_t.stop()
            query = db.text(f'SELECT COUNT(*) FROM index')
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
