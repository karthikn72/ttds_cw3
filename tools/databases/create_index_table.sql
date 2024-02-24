DROP TABLE IF EXISTS index;

CREATE TABLE index (
    word_id INTEGER REFERENCES words(word_id),
    article_id INTEGER REFERENCES articles(article_id),
    positions INTEGER[],
    tfidf INTEGER,
    PRIMARY KEY (word_id, article_id)
);