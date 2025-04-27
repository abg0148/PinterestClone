"""Signing in a new user"""
select signup_user('alice_w', 'alice@example.com', 'hash1');
select signup_user('bob_s', 'bob@example.com', 'hash2');
select signup_user('charlie_b', 'charlie@example.com', 'hash3');

"""Signup failure - username/email already exists"""
select signup_user('alice_w', 'test@example.com', 'hash1');
select signup_user('alice', 'alice@example.com', 'hash1');

"""Sign in Failure - wrong credentials"""
select signin_user('bob_s', 'hash1');

"""Sign In Success"""
select signin_user('bob_s', 'hash2');

"""Create New Profile"""
select update_profile(1, 'Alice Wonderland', 'Dreamer of dreams', null);

"""Update Profile"""
select update_profile(1, 'Alex Wonderland', 'Dreamer of dreams', null);

"""Updating Profile - Not an Active User"""
select update_profile(10, 'Alex Wonderland', 'Dreamer of dreams', null);

"""Create Boards"""
select create_board(1, 'Inspiration', 'Ideas worth pinning', false);
select create_board(1, 'Secret Stash', 'Private stuff', true);
select create_board(4, 'Bob’s Builds', 'DIY projects', false);
select create_board(5, 'Hero Gear', 'Amazonian essentials', false);

"""Create Posts"""
select create_post(1, 1, 'art,design', 'http://img.com/a1', 'http://site.com/1', NULL);
select create_post(1, 4, 'tech,code', NULL, NULL, NULL);

"""Repin an original post"""
select repin_post(2, 1);

"""Repin a pinned post"""
select repin_post(3, 3);

"""Send a Friend Request"""
call send_friend_request(1, 4);

"""Accept a Friend Request"""
call update_friend_request(1, 'accepted');

"""Sending a request to existing friends"""
call send_friend_request(1, 4);

"""Declining a Request"""
call send_friend_request(1, 5);
call update_friend_request(2, 'declined');

"""Request again to existing request"""
call send_friend_request(4, 5);

"""Create a Follow Stream"""
select create_follow_stream(1, 'My Inspiration Stream');

"""Add a new/existing Board to Follow Stream"""
select add_board_to_stream(1, 1);

"""Like a Pin"""
select like_pin(4, 1);

"""Like an already Liked Pin"""
select like_pin(4, 1);

"""Comment on a post that allows public comments"""
select comment_on_pin(4, 3, 'comment1');

"""Comment on a post that doesn't allow public comments"""
select comment_on_pin(4, 2, 'comment1');

"""Show post in reverse order"""
select repin_post(1, 2);
SELECT
    p.id AS post_id,
    pin.board_id,
    pin.created_at AS pinned_at,
    p.image_url,
    p.tags
FROM
    follow_stream_board fsb
INNER JOIN pin
    ON fsb.board_id = pin.board_id
    AND pin.terminated_at IS NULL
INNER JOIN post p
    ON pin.post_id = p.id
    AND p.terminated_at IS NULL
WHERE
    fsb.stream_id = 1
    AND fsb.deleted_at IS NULL
ORDER BY
    pin.created_at DESC;

"""Keyword Search"""
SELECT
    p.id AS post_id
FROM
    post p
WHERE
    p.terminated_at IS NULL
    AND p.tags ILIKE '%art%'
ORDER BY
    p.created_at DESC;