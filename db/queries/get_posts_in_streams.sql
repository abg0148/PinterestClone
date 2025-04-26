-- returns posts tied to a stream sorted by reverse chronological order
SELECT
    p.id AS post_id,
    pin.board_id,
    pin.created_at AS pinned_at,
    p.image_url,
    p.tags
FROM
    follow_stream_board fsb
INNER JOIN pin
    ON fsb.board_id = pin.board_id
    AND pin.terminated_at IS NULL
INNER JOIN post p
    ON pin.post_id = p.id
    AND p.terminated_at IS NULL
WHERE
    fsb.stream_id = <your_stream_id_here>
    AND fsb.deleted_at IS NULL
ORDER BY
    pin.created_at DESC;

