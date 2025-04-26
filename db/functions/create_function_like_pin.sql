-- this will internally increase the like counter for the post
CREATE OR REPLACE FUNCTION like_pin(
    _user_id INTEGER,
    _pin_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    _post_id INTEGER;
    _existing_like INTEGER;
BEGIN
    -- Step 1: Fetch the post_id tied to the pin
    SELECT post_id INTO _post_id
    FROM pin
    WHERE id = _pin_id
      AND terminated_at IS NULL;

    -- Step 2: If pin doesn't exist
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pin not found or terminated';
    END IF;

    -- Step 3: Check if like already exists
    SELECT 1 INTO _existing_like
    FROM "like"
    WHERE user_id = _user_id
      AND post_id = _post_id
      AND terminated_at IS NULL;

    IF FOUND THEN
        RETURN FALSE; -- Already liked
    END IF;

    -- Step 4: Insert like on post
    INSERT INTO "like" (user_id, post_id)
    VALUES (_user_id, _post_id);

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
