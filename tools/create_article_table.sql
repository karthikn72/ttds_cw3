
DROP TABLE IF EXISTS articles;

CREATE TABLE articles (
    date VARCHAR(100),
    year INT,
    month FLOAT,
    day INT,
    author TEXT,
    title TEXT,
    article TEXT,
    url TEXT,
    section TEXT,
    publication TEXT
);
