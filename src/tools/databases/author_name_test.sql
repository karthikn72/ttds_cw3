SELECT articles.article_id, array_agg(authors.author_name) author_names
                                    FROM articles, (select article_id, author_id FROM articles LEFT JOIN LATERAL unnest(author_ids) AS author_id ON TRUE) AS a, LEFT JOIN authors ON 
                                        articles.article_id < 10 AND
                                        a.author_id = authors.author_id AND 
                                        a.article_id = articles.article_id
                                    GROUP BY articles.article_id;