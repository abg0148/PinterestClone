CREATE OR REPLACE FUNCTION update_profile(
    _user_id INTEGER,
    _full_name VARCHAR DEFAULT NULL,
    _bio TEXT DEFAULT NULL,
    _picture BYTEA DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE "user"
    SET
        full_name = COALESCE(_full_name, full_name),
        bio = COALESCE(_bio, bio),
        picture = COALESCE(_picture, picture)
    WHERE id = _user_id
      AND terminated_at IS NULL;
END;
$$ LANGUAGE plpgsql;
