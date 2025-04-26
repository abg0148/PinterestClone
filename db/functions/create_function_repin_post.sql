-- this allows you to repin a pin to a different board
CREATE OR REPLACE FUNCTION repin_post(
    _board_id INTEGER,
    _source_pin_id INTEGER
) RETURNS INTEGER AS $$
DECLARE
    _post_id INTEGER;
    _new_pin_id INTEGER;
BEGIN
    -- Step 1: Fetch the original post_id from the source pin
    SELECT post_id INTO _post_id
    FROM pin
    WHERE id = _source_pin_id
      AND terminated_at IS NULL;

    -- Step 2: Check if source pin was valid
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Original pin does not exist or has been terminated';
    END IF;

    -- Step 3: Use create_pin to insert a new pin
    _new_pin_id := create_pin(_board_id, _post_id, _source_pin_id);

    RETURN _new_pin_id;
END;
$$ LANGUAGE plpgsql;
