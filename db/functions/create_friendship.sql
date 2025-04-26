-- Procedure to create friendship
CREATE OR REPLACE PROCEDURE create_friendship(sender_user_id INTEGER, receiver_user_id INTEGER)
AS $$
DECLARE
    user_1 INTEGER;
    user_2 INTEGER;
BEGIN
    -- Assign correct user order
    user_1 := CASE WHEN sender_user_id < receiver_user_id THEN sender_user_id ELSE receiver_user_id END;
    user_2 := CASE WHEN sender_user_id < receiver_user_id THEN receiver_user_id ELSE sender_user_id END;

    -- Check if a friendship exists
    IF EXISTS (
        SELECT 1
        FROM friend
        WHERE user_id_1 = user_1 AND user_id_2 = user_2
    ) THEN
        RAISE EXCEPTION 'Friendship already exists between these users';
    END IF;

    -- Create the friendship
    INSERT INTO friend (user_id_1, user_id_2) 
    VALUES (user_1, user_2);
END;
$$ LANGUAGE plpgsql;
