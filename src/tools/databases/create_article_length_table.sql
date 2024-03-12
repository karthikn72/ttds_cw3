DROP TABLE IF EXISTS article_length_table;

CREATE TABLE article_length_table (
    article_id INTEGER REFERENCES articles(article_id),
    doc_length INTEGER,
    PRIMARY KEY (article_id)
);