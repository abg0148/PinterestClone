CREATE OR REPLACE FUNCTION like_post(
    _user_id INTEGER,
    _post_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    _existing_like INTEGER;
BEGIN
    -- Step 1: Check if user already liked the post
    SELECT 1 INTO _existing_like
    FROM "like"
    WHERE user_id = _user_id
      AND post_id = _post_id
      AND terminated_at IS NULL;

    IF FOUND THEN
        RETURN FALSE; -- Already liked
    END IF;

    -- Step 2: Insert new like
    INSERT INTO "like" (user_id, post_id)
    VALUES (_user_id, _post_id);

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
