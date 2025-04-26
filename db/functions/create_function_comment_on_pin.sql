CREATE OR REPLACE FUNCTION comment_on_pin(
    _user_id INTEGER,
    _pin_id INTEGER,
    _body TEXT
) RETURNS INTEGER AS $$
DECLARE
    _board_id INTEGER;
    _board_owner_id INTEGER;
    _allow_public BOOLEAN;
    _new_comment_id INTEGER;
BEGIN
    -- Step 1: Fetch board info through pin
    SELECT b.id, b.user_id, b.allow_public_comments
    INTO _board_id, _board_owner_id, _allow_public
    FROM pin
    INNER JOIN board b ON pin.board_id = b.id
    WHERE pin.id = _pin_id
      AND pin.terminated_at IS NULL
      AND b.terminated_at IS NULL;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pin or Board does not exist or has been terminated';
    END IF;

    -- Step 2: Check permission
    IF NOT (_allow_public OR _board_owner_id = _user_id) THEN
        RAISE EXCEPTION 'User is not allowed to comment on this pin';
    END IF;

    -- Step 3: Insert comment
    INSERT INTO comment (user_id, pin_id, body)
    VALUES (_user_id, _pin_id, _body)
    RETURNING id INTO _new_comment_id;

    RETURN _new_comment_id;
END;
$$ LANGUAGE plpgsql;
