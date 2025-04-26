-- just in case we need to update board name, description, or toggle public comments on/off
CREATE OR REPLACE FUNCTION update_board(
    _board_id INTEGER,
    _board_name VARCHAR DEFAULT NULL,
    _description TEXT DEFAULT NULL,
    _allow_public_comments BOOLEAN DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    _updated_rows INTEGER;
BEGIN
    UPDATE board
    SET
        board_name = COALESCE(_board_name, board_name),
        description = COALESCE(_description, description),
        allow_public_comments = COALESCE(_allow_public_comments, allow_public_comments)
    WHERE id = _board_id
      AND terminated_at IS NULL;

    GET DIAGNOSTICS _updated_rows = ROW_COUNT;

    IF _updated_rows = 1 THEN
        RETURN TRUE;  -- Update succeeded
    ELSE
        RETURN FALSE; -- Board not found or terminated
    END IF;
END;
$$ LANGUAGE plpgsql;
