
BEGIN;

INSERT INTO sections (section_name)
SELECT DISTINCT section FROM articles;

UPDATE articles
SET section = s.section_id
FROM sections s
WHERE articles.section = s.section_name;

ALTER TABLE articles ALTER COLUMN section TYPE INTEGER USING section::integer;

ALTER TABLE articles
RENAME COLUMN section TO section_id;

COMMIT;
