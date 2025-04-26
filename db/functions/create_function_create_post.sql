-- this will always trigger create pin
CREATE OR REPLACE FUNCTION create_post(
    _user_id INTEGER,
    _board_id INTEGER,
    _tags VARCHAR,
    _image_url VARCHAR DEFAULT NULL,
    _source_page VARCHAR DEFAULT NULL,
    _image_blob BYTEA DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    _new_post_id INTEGER;
    _final_image_url VARCHAR;
BEGIN
    -- if no url is passed, we create a system generated one which will be unqiue to the post
    -- Step 0: Prepare final image URL
    _final_image_url := COALESCE(
        _image_url,
        CONCAT('generated-', gen_random_uuid())
    );

    -- Step 1: Insert new post
    INSERT INTO post (user_id, tags, image_url, source_page, image_blob)
    VALUES (_user_id, _tags, _final_image_url, _source_page, _image_blob)
    RETURNING id INTO _new_post_id;

    -- Step 2: Pin the new post immediately to the board
    PERFORM create_pin(_board_id, _new_post_id, NULL);

    -- Step 3: Return new post id
    RETURN _new_post_id;
END;
$$ LANGUAGE plpgsql;
