CREATE OR REPLACE PROCEDURE send_friend_request(sender_user_id INTEGER, receiver_user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    -- do not send request to self
    IF sender_user_id = receiver_user_id THEN
        RAISE EXCEPTION 'Cannot send friend request to yourself';
    END IF;

    -- check if already friends
    IF EXISTS (
        SELECT 1 
        FROM friend 
        WHERE (user_id_1 = sender_user_id AND user_id_2 = receiver_user_id) 
           OR (user_id_1 = receiver_user_id AND user_id_2 = sender_user_id)
    ) THEN 
        RAISE EXCEPTION 'Users are already friends';
    END IF;

    -- Check if a friend request already exists
    IF EXISTS (
        SELECT 1
        FROM friend_request
        WHERE (sender_id = sender_user_id AND receiver_id = receiver_user_id)
           OR (sender_id = receiver_user_id AND receiver_id = sender_user_id)
          AND status = 'pending'
    ) THEN
        RAISE EXCEPTION 'Friend request already exists between these users';
    END IF;

    -- Insert the friend request
    INSERT INTO friend_request (sender_id, receiver_id, status)
    VALUES (sender_user_id, receiver_user_id, 'pending');
END;
$$;
