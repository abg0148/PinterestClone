-- ==========================
-- USERS
-- ==========================
INSERT INTO "user" (id, username, full_name, email, password_hash, bio, picture, created_at, terminated_at) VALUES
(1, 'alice_w', 'Alice Wonderland', 'alice@example.com', 'hash1', 'Dreamer of dreams', NULL, NOW(), NULL),
(2, 'bob_s', 'Bob Stone', 'bob@example.com', 'hash2', NULL, NULL, NOW(), NULL),
(3, 'charlie_b', 'Charlie Brown', 'charlie@example.com', 'hash3', 'Just a guy', NULL, NOW(), NOW() - INTERVAL '10 days'),
(4, 'diana_p', 'Diana Prince', 'diana@example.com', 'hash4', 'Wonder vibes', NULL, NOW(), NULL),
(5, 'eve_r', 'Eve Riddle', 'eve@example.com', 'hash5', NULL, NULL, NOW(), NULL);

-- ==========================
-- BOARDS
-- ==========================
INSERT INTO board (id, user_id, board_name, description, allow_public_comments, created_at, terminated_at) VALUES
(1, 1, 'Inspiration', 'Ideas worth pinning', TRUE, NOW(), NULL),
(2, 1, 'Secret Stash', 'Private stuff', FALSE, NOW(), NULL),
(3, 2, 'Bob’s Builds', 'DIY projects', TRUE, NOW(), NULL),
(4, 4, 'Hero Gear', 'Amazonian essentials', TRUE, NOW(), NULL),
(5, 5, 'Mystery Pins', NULL, TRUE, NOW(), NOW());

-- ==========================
-- POSTS
-- ==========================
INSERT INTO post (id, user_id, tags, image_url, source_page, image_blob, created_at, terminated_at) VALUES
(1, 1, 'art,design', 'http://img.com/a1', 'http://site.com/1', NULL, NOW(), NULL),
(2, 2, 'tech,code', 'http://img.com/b2', NULL, NULL, NOW(), NULL),
(3, 3, 'food,recipe', 'http://img.com/c3', 'http://site.com/3', NULL, NOW(), NULL),
(4, 4, 'fashion,armor', 'http://img.com/d4', NULL, NULL, NOW(), NULL),
(5, 5, 'mystery,abstract', 'http://img.com/e5', NULL, NULL, NOW(), NOW());

-- ==========================
-- PINS
-- ==========================
INSERT INTO pin (id, board_id, post_id, root_pin_id, created_at, terminated_at) VALUES
(1, 1, 1, NULL, NOW(), NULL),
(2, 1, 2, NULL, NOW(), NULL),
(3, 3, 2, 2, NOW(), NULL),  -- Repin of pin 2
(4, 4, 4, NULL, NOW(), NULL),
(5, 5, 5, NULL, NOW(), NOW());  -- Terminated pin

-- ==========================
-- COMMENTS
-- ==========================
INSERT INTO comment (id, pin_id, user_id, body, created_at, deleted_at) VALUES
(1, 1, 2, 'Nice work!', NOW(), NULL),
(2, 2, 1, 'Very techy!', NOW(), NULL),
(3, 3, 3, 'Yummy', NOW(), NOW()), -- Comment from terminated user
(4, 4, 4, 'Iconic.', NOW(), NULL),
(5, 4, 5, 'Looks cool.', NOW(), NULL);

-- ==========================
-- LIKES
-- ==========================
INSERT INTO "like" (user_id, post_id, created_at, terminated_at) VALUES
(1, 2, NOW(), NULL),
(2, 1, NOW(), NULL),
(3, 1, NOW(), NULL),
(4, 4, NOW(), NULL),
(5, 3, NOW(), NOW()); -- Terminated like

-- ==========================
-- FRIEND REQUESTS
-- ==========================
INSERT INTO friend_request (id, sender_id, receiver_id, status, created_at, terminated_at) VALUES
(1, 1, 2, 'pending', NOW(), NULL),
(2, 2, 3, 'accepted', NOW(), NULL),
(3, 3, 4, 'declined', NOW(), NULL),
(4, 4, 1, 'accepted', NOW(), NULL),
(5, 5, 2, 'pending', NOW(), NULL);

-- ==========================
-- FRIENDS
-- ==========================
INSERT INTO friend (user_id_1, user_id_2, since, terminated_at) VALUES
(1, 2, NOW(), NULL),
(1, 4, NOW(), NULL),
(2, 3, NOW(), NULL),
(3, 5, NOW(), NULL),
(4, 5, NOW(), NOW()); -- Terminated friendship

-- ==========================
-- DIRECT BOARD FOLLOWS
-- ==========================
INSERT INTO follow (user_id, board_id, created_at, terminated_at) VALUES
(1, 3, NOW(), NULL),
(2, 1, NOW(), NULL),
(3, 1, NOW(), NULL),
(4, 2, NOW(), NULL),  -- Following private board
(5, 4, NOW(), NOW()); -- Terminated follow

-- ==========================
-- FOLLOW STREAMS
-- ==========================
INSERT INTO follow_stream (id, user_id, stream_name, created_at, terminated_at) VALUES
(1, 1, 'My Inspiration Stream', NOW(), NULL),
(2, 2, 'CodeLife', NOW(), NULL),
(3, 3, 'Foodies', NOW(), NULL),
(4, 4, 'WonderWorld', NOW(), NULL),
(5, 5, 'DarkMystery', NOW(), NOW());

-- ==========================
-- FOLLOW STREAM BOARDS
-- ==========================
INSERT INTO follow_stream_board (stream_id, board_id, added_at, deleted_at) VALUES
(1, 1, NOW(), NULL),
(1, 2, NOW(), NULL),
(2, 3, NOW(), NULL),
(3, 5, NOW(), NOW()), -- Terminated board
(4, 4, NOW(), NULL);
