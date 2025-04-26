CREATE OR REPLACE FUNCTION add_board_to_stream(
    _stream_id INTEGER,
    _board_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    _existing INTEGER;
BEGIN
    -- Check if already added
    SELECT 1 INTO _existing
    FROM follow_stream_board
    WHERE stream_id = _stream_id
      AND board_id = _board_id
      AND deleted_at IS NULL;

    IF FOUND THEN
        RETURN FALSE; -- Already added
    END IF;

    -- Add the board
    INSERT INTO follow_stream_board (stream_id, board_id)
    VALUES (_stream_id, _board_id);

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
