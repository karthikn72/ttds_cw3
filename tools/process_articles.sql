
BEGIN;
-- Drop irrelevant date columns
ALTER TABLE articles DROP COLUMN year, DROP COLUMN month, DROP COLUMN day;

-- Rename date column
ALTER TABLE articles
   RENAME COLUMN date TO upload_date;

-- Convert date column to timestamp
ALTER TABLE articles
   ALTER COLUMN upload_date TYPE TIMESTAMP USING TO_TIMESTAMP(upload_date, 'YYYY-MM-DD HH24:MI:SS');

-- Remove special characters from title column
UPDATE articles
SET title = REPLACE(REPLACE(title, E'\n', ''), E'\r', '');

-- Remove code and other special characters from article text
UPDATE articles
SET article = REPLACE(REPLACE(REGEXP_REPLACE(article, '\{[^}]+\}', '', 'g'), E'\n', ''), E'\r', '');

-- Remove articles with less than 500 characters
DELETE FROM articles
WHERE LENGTH(article) < 500;

COMMIT;
