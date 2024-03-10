CREATE TABLE index_table (
    article_id INTEGER REFERENCES articles(article_id),
    doc_length INTEGER,
    PRIMARY KEY (article_id)
);