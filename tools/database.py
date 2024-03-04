import os
import timer
import random
from datetime import datetime
import pandas as pd
from tqdm import tqdm

import sqlalchemy as db
from sqlalchemy.dialects.postgresql import insert, ARRAY, INTEGER

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

    def get_publications(self):
        query = db.text('SELECT publication_name FROM publications')
        with self.engine.connect() as db_conn:
            t = timer.Timer("Got results in {:.4f}s")
            t.start()
            results = db_conn.execute(query)
            pubs = [row.publication_name for row in results]
            t.stop()
            return pubs
    
    def get_articles(self,
                     article_ids: list[int] = None,
                     start_date: datetime = None,
                     end_date: datetime = None,
                     sections: list[str] = None,
                     publications: list[str] = None,
                     limit=10,
                     offset=0,
                     ):
        base_query_1 = f'SELECT articles.article_id, upload_date, auth.author_names, title, article, url, s.section_name, p.publication_name \
                                    FROM articles \
                                    LEFT JOIN \
                                        sections s \
                                    ON \
                                        articles.section_id = s.section_id \
                                    LEFT JOIN \
                                        (SELECT a.article_id, ARRAY_AGG(authors.author_name) as author_names \
                                         FROM'
        base_query_2 = f'(SELECT article_id, unnest(author_ids) as author_id FROM articles) a'
        base_query_3 = f'LEFT JOIN authors ON a.author_id = authors.author_id GROUP BY a.article_id) auth \
                                    ON \
                                        articles.article_id = auth.article_id \
                                    LEFT JOIN \
                                        publications p \
                                    ON \
                                        articles.publication_id = p.publication_id'
        add_queries = []
        if article_ids:
            article_ids = tuple(article_ids) if len(article_ids) > 1 else f'({article_ids[0]})'
            base_query_2 = f'(SELECT article_id, unnest(author_ids) as author_id FROM articles WHERE articles.article_id IN {article_ids}) a'
            add_queries.append(f'articles.article_id IN {article_ids}')
        if sections:
            sections = tuple(sections) if len(sections) > 1 else f'(\'{sections[0]}\')'
            add_queries.append(f's.section_name IN {sections}')
        if publications:
            publications = tuple(publications) if len(publications) > 1 else f'(\'{publications[0]}\')'
            add_queries.append(f'p.publication_name IN {publications}')
        if start_date:
            start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
            add_queries.append(f"upload_date >= TIMESTAMP \'{start_date}\'")
        if end_date:
            end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
            add_queries.append(f"upload_date <= TIMESTAMP \'{end_date}\'")
        base_query = ' '.join([base_query_1, base_query_2, base_query_3]) + ' '
        if add_queries:
            base_query += 'WHERE ' + ' AND '.join(add_queries) + ' '
        
        base_query += f'LIMIT {limit} OFFSET {offset}'
        query = db.text(base_query)
        with self.engine.connect() as db_conn:
            t = timer.Timer("Got results in {:.4f}s")
            t.start()
            article_df = db_conn.execute(query)
            article_df = pd.DataFrame(article_df)
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

    def add_words(self, index, conn):
        self.words = db.Table('words', self.metadata, autoload_with=self.engine)
        word_list = [{'word':word} for word in index['word'].unique()]
        chunk_size = 1000
        for i in range(0, len(word_list), chunk_size):
            chunk = word_list[i:i+chunk_size]
            query = insert(self.words).values(word_list).on_conflict_do_nothing()
        t = timer.Timer('Inserted words in {:.4f}s')
        t.start()
        conn.execute(query)
        t.stop()
        query = db.text(f'SELECT * FROM words WHERE word in {tuple(index.word.unique())};')
        t = timer.Timer('Got words in {:.4f}s')
        t.start()
        word_df = pd.read_sql(query, conn)
        t.stop()
        return word_df

    def add_index(self, index, conn):
        t = timer.Timer('Built index in {:.4f}s')
        t.start()
        index.to_sql('index_table', conn, if_exists='append', chunksize=10000, index=False, dtype={'article_id':INTEGER, 'positions':ARRAY(INTEGER), 'word_id':INTEGER}, method='multi')
        t.stop()

    def calc_tfidf(self, conn):
        sql_path = "tools/databases/calc_tfidf.sql"
        with open(sql_path) as file:
            query = db.text(file.read())
            t = timer.Timer('Calculated tfidf in {:.4f}s')
            t.start()
            conn.execute(query)
            t.stop()

    def build_index(self, index: pd.DataFrame):
        with self.engine.connect() as db_conn:
            try:
                word_df = self.add_words(index=index, conn=db_conn)
                index = pd.merge(index, word_df, on='word', how='left')
                index = index.drop('word', axis=1)
                self.add_index(index=index, conn=db_conn)
                db_conn.commit()
                return "Index build successful"
            except Exception as e:
                db_conn.rollback()
                print("!!!!! CANCELLED INDEXING !!!!!")
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
                if confirm == 'y':
                    with self.engine.connect() as db_conn:
                        for sql_path in sql_paths:
                            with open(sql_path) as file:
                                query = db.text(file.read())
                                db_conn.execute(query)
                        db_conn.commit()
                    print("Index reset")
                else:
                    print("Cancelled index reset")
                return
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
                
                