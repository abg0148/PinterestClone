CREATE OR REPLACE FUNCTION create_follow_stream(
    _user_id INTEGER,
    _stream_name VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    _new_stream_id INTEGER;
BEGIN
    INSERT INTO follow_stream (user_id, stream_name)
    VALUES (_user_id, _stream_name)
    RETURNING id INTO _new_stream_id;

    RETURN _new_stream_id;
END;
$$ LANGUAGE plpgsql;
