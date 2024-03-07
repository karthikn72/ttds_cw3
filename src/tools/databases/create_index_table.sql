DROP TABLE IF EXISTS index_table;

CREATE TABLE index_table (
    word_id INTEGER REFERENCES words(word_id),
    article_id INTEGER REFERENCES articles(article_id),
    positions INTEGER[],
    tfidf float,
    PRIMARY KEY (word_id, article_id)
);