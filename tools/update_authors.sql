
BEGIN;

-- Convert author column to array
ALTER TABLE articles
    SET author = string_to_array(author, ', ');

INSERT INTO authors (author_name)
SELECT DISTINCT UNNEST(author) FROM articles;

-- Update the articles table with author IDs
UPDATE articles
SET author = (
    SELECT ARRAY_AGG(author_id)
    FROM authors
    WHERE author_name = ANY(articles.author)
);

COMMIT;