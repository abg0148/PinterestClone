CREATE OR REPLACE PROCEDURE update_friend_request(sender_user_id INTEGER, receiver_user_id INTEGER, _status VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if the request exists
    IF EXISTS (
        SELECT 1
        FROM friend_request
        WHERE sender_id = sender_user_id AND receiver_id = receiver_user_id
    ) THEN
        -- Update the friend request status
        UPDATE friend_request
        SET status = _status
        WHERE sender_id = sender_user_id AND receiver_id = receiver_user_id;

        -- If accepted, create the friendship
        IF _status = 'accepted' THEN
            CALL create_friendship(sender_user_id, receiver_user_id);
        END IF;
    ELSE
        RAISE EXCEPTION 'Friend request does not exist';
    END IF;
END;
$$;
