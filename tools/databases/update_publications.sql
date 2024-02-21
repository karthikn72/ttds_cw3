
BEGIN;

INSERT INTO publications (publication_name)
SELECT DISTINCT publication FROM articles;

UPDATE articles
SET publication = p.publication_id
FROM publications p
WHERE articles.publication = p.publication_name;

ALTER TABLE articles ALTER COLUMN publication TYPE INTEGER USING publication::integer;

ALTER TABLE articles
RENAME COLUMN publication TO publication_id;

COMMIT;
