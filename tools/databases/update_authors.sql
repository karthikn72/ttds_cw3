
BEGIN;

-- Convert author column to array
ALTER TABLE articles
ALTER COLUMN author TYPE text[] USING string_to_array(author, ', ')::text[];

INSERT INTO authors (author_name)
SELECT DISTINCT UNNEST(author::text[]) FROM articles;

-- Update the articles table with author IDs
UPDATE articles
SET author = (
    SELECT ARRAY_AGG(author_id)
    FROM authors
    WHERE author_name = ANY(articles.author)
);

ALTER TABLE articles
ALTER COLUMN author TYPE integer[] USING author::integer[];

ALTER TABLE articles
RENAME COLUMN author TO author_ids;

DELETE FROM 
    authors 
WHERE 
    author_name ~ '[^a-zA-Z0-9\-àÀáÁâÂãÃäÄåÅāĀăĂąĄèÈéÉêÊëËēĒĕĔěĚęĘìÌíÍîÎïÏīĪįĮòÒóÓôÔõÕöÖøØōŌùÙúÚûÛüÜūŪůŮýÝÿ.'', ]';

COMMIT;
