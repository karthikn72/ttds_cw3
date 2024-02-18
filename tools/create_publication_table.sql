DROP TABLE IF EXISTS publications;

CREATE TABLE publications (
    publication_id SERIAL PRIMARY KEY,
    publication_name VARCHAR(255) UNIQUE NOT NULL
);