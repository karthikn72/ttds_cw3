import os

from google.cloud.sql.connector import Connector, IPTypes
import pg8000

import sqlalchemy as db

def connect_with_connector() -> db.engine.base.Engine:
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

    pool = db.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    print("Connected to database successfully")
    return pool 

with connect_with_connector().connect() as db_conn:
    metadata = db.MetaData()
    print(metadata)
    Articles = db.Table('Articles', metadata,
                db.Column('Id', db.Integer(),primary_key=True),
                db.Column('Author', db.String(255), nullable=True),
                db.Column('Title', db.String(500), nullable=False),
                db.Column('Article', db.String(), nullable=False),
                db.Column('URL', db.String(), nullable=True),
                db.Column('Section', db.String(), nullable=False),
                db.Column('Publication', db.String(), nullable=False)
                )

    metadata.create_all(db_conn)
    query = db.insert(Articles).values(Id=1, Author='John', Title='The Great Escape', Article='Yeetus feetus lorem ipsum', URL='yeet', Section='Sports', Publication='Guardian')
    result = db_conn.execute(query)
    output = db_conn.execute(Articles.select()).fetchall()
    print(output)
    print(metadata.tables.keys())
