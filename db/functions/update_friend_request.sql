CREATE OR REPLACE PROCEDURE update_friend_request(request_id INTEGER, _status VARCHAR)
LANGUAGE plpgsql
AS $$
DECLARE
    _sender_id INTEGER;
    _receiver_id INTEGER;
BEGIN
    -- Check that status is only 'accepted' or 'declined'
    IF _status NOT IN ('accepted', 'declined') THEN
        RAISE EXCEPTION 'Status must be accepted or declined';
    END IF;

    -- Check if the request exists and is still active
    IF EXISTS (
        SELECT 1
        FROM friend_request
        WHERE id = request_id
          AND terminated_at IS NULL
    ) THEN
        -- Fetch sender_id and receiver_id from the request
        SELECT sender_id, receiver_id
        INTO _sender_id, _receiver_id
        FROM friend_request
        WHERE id = request_id;

        -- Update the friend request
        UPDATE friend_request
        SET status = _status, terminated_at = CURRENT_TIMESTAMP
        WHERE id = request_id;

        -- If accepted, create the friendship
        IF _status = 'accepted' THEN
            CALL create_friendship(_sender_id, _receiver_id);
        END IF;
    ELSE
        RAISE EXCEPTION 'Friend request does not exist or is already terminated';
    END IF;
END;
$$;
