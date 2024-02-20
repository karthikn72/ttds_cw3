
BEGIN;

INSERT INTO publications (publication_name)
SELECT DISTINCT publication FROM articles;

UPDATE articles
SET publication = p.publication_id
FROM publications p
WHERE articles.publication = p.publication_name;

COMMIT;
