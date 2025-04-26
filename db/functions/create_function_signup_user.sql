CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- user signup prodcedure
CREATE OR REPLACE FUNCTION signup_user(
    _username VARCHAR,
    _email VARCHAR,
    _plain_password VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    _new_user_id INTEGER;
BEGIN
    INSERT INTO "user" (username, email, password_hash)
    VALUES (_username, _email, crypt(_plain_password, gen_salt('bf')))
    RETURNING id INTO _new_user_id;

    RETURN _new_user_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Username or email already exists';
END;
$$ LANGUAGE plpgsql;
