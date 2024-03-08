import os
import timer
import random
from datetime import datetime
import pandas as pd
from tqdm import tqdm

import sqlalchemy as db
from sqlalchemy.dialects.postgresql import insert, ARRAY, INTEGER, TIMESTAMP

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

    def get_publications(self):
        query = db.text('SELECT publication_name FROM publications')
        with self.engine.connect() as db_conn:
            t = timer.Timer("Got results in {:.4f}s")
            t.start()
            results = db_conn.execute(query)
            pubs = [row.publication_name for row in results]
            t.stop()
            return pubs
    
    def add_authors(self, articles, conn):
        self.authors = db.Table('authors', self.metadata, autoload_with=self.engine)
        author_list = [{'author_name':author} for author in articles.author.unique()]
        chunk_size = 1000
        for i in range(0, len(author_list), chunk_size):
            chunk = author_list[i:i+chunk_size]
            query = insert(self.authors).values(chunk).on_conflict_do_nothing()
        t = timer.Timer('Inserted authors in {:.4f}s')
        t.start()
        conn.execute(query)
        t.stop()
        authors = articles.author.dropna().unique()
        authors = tuple(authors) if len(authors) > 1 else f'(\'{authors[0]}\')'
        query = db.text(f'SELECT author_id, author_name as author FROM authors WHERE author_name in {authors};')
        t = timer.Timer('Got authors in {:.4f}s')
        t.start()
        author_df = conn.execute(query)
        author_df = pd.DataFrame(author_df)
        t.stop()
        return author_df
    
    def add_sections(self, articles, conn, get_ids=True):
        self.sections = db.Table('sections', self.metadata, autoload_with=self.engine)
        section_list = [{'section_name':section} for section in articles.section.unique()]
        chunk_size = 1000
        for i in range(0, len(section_list), chunk_size):
            chunk = section_list[i:i+chunk_size]
            query = insert(self.sections).values(chunk).on_conflict_do_nothing()
        t = timer.Timer('Inserted sections in {:.4f}s')
        t.start()
        conn.execute(query)
        t.stop()
        if get_ids:
            sections = articles.section.dropna().unique()
            sections = tuple(sections) if len(sections) > 1 else f'(\'{sections[0]}\')'
            query = db.text(f'SELECT section_id, section_name as section FROM sections WHERE section_name in {sections};')
            t = timer.Timer('Got sections in {:.4f}s')
            t.start()
            section_df = conn.execute(query)
            section_df = pd.DataFrame(section_df)
            t.stop()
            return section_df
    
    def add_publications(self, articles, conn):
        self.publications = db.Table('publications', self.metadata, autoload_with=self.engine)
        publication_list = [{'publication_name':publication} for publication in articles.publication.unique()]
        chunk_size = 1000
        for i in range(0, len(publication_list), chunk_size):
            chunk = publication_list[i:i+chunk_size]
            query = insert(self.publications).values(chunk).on_conflict_do_nothing()
        t = timer.Timer('Inserted publications in {:.4f}s')
        t.start()
        conn.execute(query)
        t.stop()
        publications = articles.publication.dropna().unique()
        publications = tuple(publications) if len(publications) > 1 else f'(\'{publications[0]}\')'
        query = db.text(f'SELECT publication_id, publication_name as publication FROM publications WHERE publication_name in {publications};')
        t = timer.Timer('Got publications in {:.4f}s')
        t.start()
        publication_df = conn.execute(query)
        publication_df = pd.DataFrame(publication_df)
        t.stop()
        return publication_df
    
    def add_articles(self, articles: pd.DataFrame, test=True):
        with self.engine.connect() as db_conn:
            try:
                author_df = self.add_authors(articles=articles, conn=db_conn)
                articles = pd.merge(articles, author_df, on='author', how='left')
                articles['author_ids'] = articles['author_id'].apply(lambda x: [x])
                articles = articles.drop(['author', 'author_id'], axis=1)
                
                section_df = self.add_sections(articles=articles, conn=db_conn)
                articles = pd.merge(articles, section_df, on='section', how='left')
                articles = articles.drop(['section'], axis=1)
                
                publication_df = self.add_publications(articles=articles, conn=db_conn)
                articles = pd.merge(articles, publication_df, on='publication', how='left')
                articles = articles.drop(['publication'], axis=1)
                
                t = timer.Timer('Added articles in {:.4f}s')
                t.start()
                chunk_size = 10000
                if 'imageURL' in articles.columns:
                    articles = articles.drop(['imageURL'], axis=1)
                articles.to_sql('articles', 
                                db_conn, 
                                if_exists='append', 
                                chunksize=10000, 
                                index=False, 
                                dtype={'upload_date':TIMESTAMP,
                                        'author_ids':ARRAY(INTEGER)
                                        }, 
                                method='multi')
                t.stop()
                db_conn.commit()
                return "Added articles successfully"
            except Exception as e:
                db_conn.rollback()
                print("!!!!! CANCELLED ADDING ARTICLES !!!!!")
                raise e
        
    def get_articles(self,
                     article_ids: list[int] = None,
                     start_date: datetime = None,
                     end_date: datetime = None,
                     add_start_date: datetime = None,
                     add_end_date: datetime = None,
                     sections: list[str] = None,
                     publications: list[str] = None,
                     sort_by_date = None,
                     limit=10,
                     offset=0,
                     ):
        base_query_1 = f'SELECT articles.article_id, upload_date, auth.author_names, title, article, url, s.section_name, p.publication_name, positive, negative, neutral \
                                    FROM articles \
                                    LEFT JOIN \
                                        sections s \
                                    ON \
                                        articles.section_id = s.section_id \
                                    LEFT JOIN \
                                        (SELECT a.article_id, ARRAY_AGG(authors.author_name) as author_names \
                                         FROM'
        base_query_2 =                      f'(SELECT article_id, unnest(author_ids) as author_id FROM articles) a'
        base_query_3 =                      f'LEFT JOIN authors ON a.author_id = authors.author_id GROUP BY a.article_id) auth \
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
        if add_start_date:
            add_start_date = add_start_date.strftime('%Y-%m-%d %H:%M:%S')
            add_queries.append(f"added_date >= TIMESTAMP \'{add_start_date}\'")
        if add_end_date:
            add_end_date = add_end_date.strftime('%Y-%m-%d %H:%M:%S')
            add_queries.append(f"added_date <= TIMESTAMP \'{add_end_date}\'")
        base_query = ' '.join([base_query_1, base_query_2, base_query_3]) + ' '

        if add_queries:
            base_query += 'WHERE ' + ' AND '.join(add_queries) + ' '

        if sort_by_date == 'asc':
            base_query += 'ORDER BY upload_date ASC '
        elif sort_by_date == 'desc':
            base_query += 'ORDER BY upload_date DESC '
        base_query += f'LIMIT {limit} OFFSET {offset}'
        query = db.text(base_query)
        with self.engine.connect() as db_conn:
            t = timer.Timer("Got results in {:.4f}s")
            # test = db_conn.execute(db.text('explain ' + base_query))
            # for line in test.fetchall():
            #     print(line)
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

    def update_sentiments(self, sentiments: pd.DataFrame, reset_sentiments=False):
        query = db.text(f'UPDATE articles \
                        SET positive = :positive, negative = :negative, neutral= :neutral \
                        WHERE article_id = :article_id')
        with self.engine.connect() as db_conn:
            try:
                if reset_sentiments:
                    self.reset_sentiments(db_conn)
                t = timer.Timer("Updated sentiments in {:.4f}s")
                t.start()
                db_conn.execute(query, sentiments.to_dict(orient="records"))
                db_conn.commit()
                t.stop()
                print("Updated sentiments!")
            except Exception as e:
                db_conn.rollback()
                print("!!!!! CANCELLED SENTIMENT UPDATE !!!!!")
                raise e

    def update_sections(self, section_df, reset_sections=False):
        query = db.text(f'UPDATE articles SET section_id = s.section_id \
                        FROM sections s \
                        WHERE s.section_name = :section AND articles.article_id = :article_id')
        with self.engine.connect() as db_conn:
            try:
                if reset_sections:
                    self.reset_sections(db_conn)
                self.add_sections(section_df, db_conn, get_ids=False)
                t = timer.Timer("Updated sections in {:.4f}s")
                t.start()
                db_conn.execute(query, section_df.to_dict(orient="records"))
                db_conn.commit()
                t.stop()
            except Exception as e:
                db_conn.rollback()
                print("!!!!! CANCELLED SECTION UPDATE !!!!!")
                raise e
            
    def add_words(self, index, conn):
        self.words = db.Table('words', self.metadata, autoload_with=self.engine)
        word_list = [{'word':word} for word in index.word.unique()]
        chunk_size = 1000
        for i in range(0, len(word_list), chunk_size):
            chunk = word_list[i:i+chunk_size]
            query = insert(self.words).values(chunk).on_conflict_do_nothing()
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

    def add_index(self, index_table, conn):
        t = timer.Timer('Built index in {:.4f}s')
        t.start()
        chunk_size = 10000
        for i in range(0, len(index_table), chunk_size):
            chunk = index_table.iloc[i:i+chunk_size,]
            chunk.to_sql('index_table', 
                        conn, 
                        if_exists='append', 
                        index=False, 
                        dtype={'article_id':INTEGER, 
                                'positions':ARRAY(INTEGER), 
                                'word_id':INTEGER}, 
                        method='multi')
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
                index = pd.merge(index, word_df, on='word', how='inner')
                index = index.drop('word', axis=1)
                self.add_index(index_table=index, conn=db_conn)
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
            words = tuple(words) if len(words) > 1 else f'(\'{(words[0])}\')'
            query = f"SELECT w.word, article_id, positions, tfidf FROM index_table, words w WHERE index_table.word_id = w.word_id AND w.word IN {words}"
            t = timer.Timer("Got index in {:.4f}s")
            t.start()
            index_df = db_conn.execute(db.text(query))
            index_df = pd.DataFrame(index_df)
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

    def reset_sections(self, conn = None):
        while True:
            confirm = input("Are you sure you want to reset the sections table? (y/n): ").lower()
            if confirm == 'y':
                if conn:
                    query = db.text('DROP TABLE sections CASCADE')
                    conn.execute(query)
                    conn.commit()
                    return "Sections reset"
                else:
                    with self.engine.connect() as conn:
                        query = db.text('DROP TABLE sections CASCADE')
                        conn.execute(query)
                        conn.commit()
                        return "Reset sections"
            elif confirm == 'n':
                return "Sections not reset"
    
    def reset_sentiments(self, conn = None):
        while True:
            confirm = input("Are you sure you want to reset the sentiments? (y/n): ").lower()
            if confirm == 'y':
                if conn:
                    query = db.text('UPDATE articles SET positive = 0, negative = 0, neutral = 0')
                    conn.execute(query)
                    conn.commit()
                    return "Reset sentiments"
                else:
                    with self.engine.connect() as conn:
                        query = db.text('UPDATE articles SET positive = 0, negative = 0, neutral = 0')
                        conn.execute(query)
                        conn.commit()
                        return "Reset sentiments"
            elif confirm == 'n':
                return "Sentiments not reset"


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
                
                