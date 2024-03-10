DROP TABLE IF EXISTS sections;

CREATE TABLE sections (
    section_id SERIAL PRIMARY KEY,
    section_name VARCHAR(255) UNIQUE
);