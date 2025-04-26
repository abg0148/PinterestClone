-- creating board, you'll need user id to do this
CREATE OR REPLACE FUNCTION create_board(
    _user_id INTEGER,
    _board_name VARCHAR,
    _description TEXT DEFAULT NULL,
    _allow_public_comments BOOLEAN DEFAULT TRUE
) RETURNS INTEGER AS $$
DECLARE
    _new_board_id INTEGER;
BEGIN
    INSERT INTO board (user_id, board_name, description, allow_public_comments)
    VALUES (_user_id, _board_name, _description, _allow_public_comments)
    RETURNING id INTO _new_board_id;

    RETURN _new_board_id;
END;
$$ LANGUAGE plpgsql;

