
DO $$
DECLARE
    n INT;

BEGIN

SELECT COUNT(DISTINCT article_id) INTO n
FROM index_table;

CREATE TEMPORARY TABLE temp_tfidf AS (
    -- Your previous TF-IDF calculation query
    WITH tf_table AS (
        SELECT
            word_id,
            article_id,
            COUNT(*) AS tf
        FROM
            (SELECT word_id, article_id,  unnest(positions) FROM index_table) AS it
        GROUP BY
            word_id, article_id
    )
    , df_table AS (
        SELECT
            word_id,
            COUNT(article_id) AS df
        FROM
            index_table
        GROUP BY
            word_id
    )
    , idf_table AS (
        SELECT
            d.word_id,
            LOG(n::decimal / (d.df + 1)) AS idf
        FROM
            df_table d, index_table i
        WHERE
            d.word_id = i.word_id
        GROUP BY
            d.word_id, d.df
    )
    SELECT
        tf.word_id,
        tf.article_id,
        tf.tf::decimal * idf.idf AS tfidf
    FROM
        tf_table tf
    JOIN
        idf_table idf ON tf.word_id = idf.word_id
);

-- Step 2: Add the TF-IDF values to the initial table
UPDATE index_table i
SET tfidf = temp_tfidf.tfidf
FROM temp_tfidf
WHERE i.word_id = temp_tfidf.word_id
    AND i.article_id = temp_tfidf.article_id;

-- Drop the temporary table
DROP TABLE temp_tfidf;
END $$;