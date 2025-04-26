-- this will only be called from inside create_post
CREATE OR REPLACE FUNCTION create_pin(
    _board_id INTEGER,
    _post_id INTEGER,
    _root_pin_id INTEGER DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    _new_pin_id INTEGER;
BEGIN
    INSERT INTO pin (board_id, post_id, root_pin_id)
    VALUES (_board_id, _post_id, _root_pin_id)
    RETURNING id INTO _new_pin_id;

    RETURN _new_pin_id;
END;
$$ LANGUAGE plpgsql;
