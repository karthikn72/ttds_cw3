DROP TABLE IF EXISTS doc_length_table;

CREATE TABLE doc_length_table (
    article_id INTEGER REFERENCES articles(article_id),
    doc_length INTEGER,
    PRIMARY KEY (article_id)
);