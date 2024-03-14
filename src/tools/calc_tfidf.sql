DO $$

DECLARE
    n INT;
    offset_val INT;
    chunk_size INT;
BEGIN

-- Step 1: Get the total count of distinct article_ids
DROP TABLE IF EXISTS article_ids;
CREATE TABLE article_ids AS SELECT DISTINCT article_id FROM index_table;
SELECT COUNT(article_id) INTO n FROM article_ids;

-- Set the chunk size (adjust as needed)
chunk_size := 1000;
offset_val := 224000;
-- Loop through chunks of data
WHILE offset_val < n LOOP
    -- Step 2: Add the TF-IDF values to the initial table for the current chunk
    RAISE NOTICE 'Time Started: %', now();
    UPDATE index_table i
    SET tfidf = temp_tfidf.tfidf
    FROM (
        -- Your previous TF-IDF calculation query for the current chunk
        WITH article_chunk AS (
            SELECT article_id FROM article_ids LIMIT chunk_size OFFSET offset_val
        )
        , log_tf_table AS (
            SELECT
                word_id,
                article_id,
                LOG(COUNT(*)) + 1 AS log_tf
            FROM (
                SELECT word_id, it2.article_id, unnest(positions)
                FROM index_table it2, article_chunk a
                WHERE it2.article_id = a.article_id
            ) AS it
            GROUP BY word_id, article_id
        )
        , idf_table AS (
            SELECT
                word_id,
                LOG(n::decimal / COUNT(article_id)) AS idf
            FROM (
                SELECT word_id, it2.article_id
                FROM index_table it2, article_chunk a
                WHERE it2.article_id = a.article_id
               ) AS it
            GROUP BY word_id
        )
        SELECT
            tf.word_id,
            tf.article_id,
            tf.log_tf::float * idf.idf AS tfidf
        FROM log_tf_table tf
        JOIN idf_table idf ON tf.word_id = idf.word_id
    ) AS temp_tfidf
    WHERE i.word_id = temp_tfidf.word_id
    AND i.article_id = temp_tfidf.article_id;
    COMMIT;
    -- Move to the next chunk
    offset_val := offset_val + chunk_size;
    RAISE NOTICE 'Time ended: %', now();
    RAISE NOTICE 'Documents calculated: %', offset_val;
END LOOP;

END $$;
