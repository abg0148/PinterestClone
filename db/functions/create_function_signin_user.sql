-- user signin procedure, need correct combination of either username and password, or email and password
CREATE OR REPLACE FUNCTION signin_user(
    _username_or_email VARCHAR,
    _plain_password VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    _db_password TEXT;
    _user_id INTEGER;
BEGIN
    SELECT id, password_hash
    INTO _user_id, _db_password
    FROM "user"
    WHERE (username = _username_or_email OR email = _username_or_email)
      AND terminated_at IS NULL
    LIMIT 1;

    -- If no user found OR password does not match
    IF NOT FOUND OR NOT (crypt(_plain_password, _db_password) = _db_password) THEN
        RAISE EXCEPTION 'Invalid credentials';
    END IF;

    RETURN _user_id;
END;
$$ LANGUAGE plpgsql;
