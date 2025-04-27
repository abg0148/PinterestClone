-- filter posts by tags in reverse chronological order
SELECT
    p.id AS post_id
FROM
    post p
WHERE
    p.terminated_at IS NULL
    AND p.tags ILIKE <your_keyword_here>
ORDER BY
    p.created_at DESC;
