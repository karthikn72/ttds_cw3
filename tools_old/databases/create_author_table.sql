
DROP TABLE IF EXISTS authors;

CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    author_name VARCHAR(255) UNIQUE NOT NULL
);