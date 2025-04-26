-- updates user profile, if user id is valid -- returns true, else return false
CREATE OR REPLACE FUNCTION update_profile(
    _user_id INTEGER,
    _full_name VARCHAR DEFAULT NULL,
    _bio TEXT DEFAULT NULL,
    _picture BYTEA DEFAULT NULL
) RETURNS BOOLEAN AS $$
DECLARE
    _updated_rows INTEGER;
BEGIN
    UPDATE "user"
    SET
        full_name = COALESCE(_full_name, full_name),
        bio = COALESCE(_bio, bio),
        picture = COALESCE(_picture, picture)
    WHERE id = _user_id
      AND terminated_at IS NULL;

    GET DIAGNOSTICS _updated_rows = ROW_COUNT;

    IF _updated_rows = 1 THEN
        RETURN TRUE;  -- Update succeeded
    ELSE
        RETURN FALSE; -- No active user found or user is terminated
    END IF;
END;
$$ LANGUAGE plpgsql;
