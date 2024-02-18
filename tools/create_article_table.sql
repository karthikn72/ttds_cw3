
DROP TABLE articles;

CREATE TABLE articles (
    date VARCHAR(20),
    year INT,
    month INT,
    day INT,
    author VARCHAR(255),
    title VARCHAR(255),
    article TEXT,
    url VARCHAR(255),
    section VARCHAR(255),
    publication VARCHAR(255)
);
