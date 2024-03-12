DO $$
DECLARE
    n INT; -- Total number of documents
    avgdl FLOAT; -- Average document length
    k1 CONSTANT FLOAT := 1.2;
    b CONSTANT FLOAT := 0.75;
BEGIN
    -- Calculate total number of documents
    SELECT AVG(doc_length) INTO avgdl
    FROM article_length_table;

    SELECT COUNT(*) INTO n
    FROM article_length_table;

    -- Creating a temporary table for BM25 scores
    CREATE TEMPORARY TABLE temp_BM25 AS (
        WITH log_tf_table AS (
            SELECT
                word_id,
                article_id,
                LOG(COUNT(*)) + 1 AS log_tf,
                COUNT(*) AS tf
            FROM
                (SELECT word_id, article_id, unnest(positions) FROM index_table) AS it
            GROUP BY
                word_id, article_id
        ),
        idf_table AS (
            SELECT
                word_id,
                LOG((n::decimal - COUNT(article_id) + 0.5) / (COUNT(article_id) + 0.5)+1) AS idf
            FROM
                index_table
            GROUP BY
                word_id
        ),
        doc_length_table AS (
            SELECT
                article_id,
                doc_length
            FROM
                article_length_table
        )

        SELECT
            tf.word_id,
            tf.article_id,
            idf.idf * (tf.tf * (k1 + 1)) / (tf.tf + k1 * (1 - b + b * (dl.doc_length / avgdl))) AS bm25
        FROM
            log_tf_table tf
        JOIN
            idf_table idf ON tf.word_id = idf.word_id
        JOIN
            doc_length_table dl ON tf.article_id = dl.article_id
    );

    -- Assuming you need to update index_table or another table with BM25 values,
    -- replace the following section with the appropriate table and column names.
    UPDATE index_table i
    SET bm25 = temp_bm25.bm25
    FROM temp_bm25
    WHERE i.word_id = temp_bm25.word_id
        AND i.article_id = temp_bm25.article_id;

    -- Clean up the temporary table
    DROP TABLE temp_bm25;
END $$;