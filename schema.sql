-- ==========================
--  USERS
-- ==========================
CREATE TABLE "user" (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(50)  UNIQUE NOT NULL,
    full_name       VARCHAR(120),
    email           VARCHAR(120) UNIQUE NOT NULL,
    password_hash   TEXT         NOT NULL,
    bio             TEXT,
    picture         BYTEA,             -- blob
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at   TIMESTAMP
);

-- ==========================
--  BOARDS (owned by users)
-- ==========================
CREATE TABLE board (
    id                   SERIAL PRIMARY KEY,
    user_id              INTEGER      NOT NULL,
    board_name           VARCHAR(120) NOT NULL,
    description          TEXT,
    allow_public_comments BOOLEAN     DEFAULT TRUE,
    created_at           TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at        TIMESTAMP,
    FOREIGN KEY (user_id)  REFERENCES "user"(id) ON DELETE CASCADE,
    UNIQUE (user_id, board_name)                -- optional: one name per user
);

-- ==========================
--  POSTS (created by users)
-- ==========================
CREATE TABLE post (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER      NOT NULL,
    tags          TEXT         NOT NULL,  -- consider normalizing later
    image_url     TEXT         NOT NULL UNIQUE,
    source_page   TEXT,
    image_blob    BYTEA,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- ==========================
--  PINS  (post placed on a board)
-- ==========================
CREATE TABLE pin (
    id             SERIAL PRIMARY KEY,
    board_id       INTEGER      NOT NULL,
    post_id        INTEGER      NOT NULL,
    root_pin_id    INTEGER,               -- nullable self-ref for repins
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at  TIMESTAMP,
    FOREIGN KEY (board_id)    REFERENCES board(id)       ON DELETE CASCADE,
    FOREIGN KEY (post_id)     REFERENCES post(id)        ON DELETE CASCADE,
    FOREIGN KEY (root_pin_id) REFERENCES pin(id)         ON DELETE SET NULL,
    UNIQUE (board_id, post_id)             -- prevents double-pinning
);

-- ==========================
--  COMMENTS  (on a pin)
-- ==========================
CREATE TABLE comment (
    id          SERIAL PRIMARY KEY,
    pin_id      INTEGER   NOT NULL,
    user_id     INTEGER   NOT NULL,
    body        TEXT      NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  TIMESTAMP,
    FOREIGN KEY (pin_id)  REFERENCES pin(id)   ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES "user"(id)
);

-- ==========================
--  LIKES  (user ↔ post)
-- ==========================
CREATE TABLE "like" (
    user_id     INTEGER   NOT NULL,
    post_id     INTEGER   NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TIMESTAMP,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES post(id)   ON DELETE CASCADE
);

-- ==========================
--  FRIEND REQUESTS
-- ==========================
CREATE TABLE friend_request (
    id           SERIAL PRIMARY KEY,
    sender_id    INTEGER   NOT NULL,
    receiver_id  INTEGER   NOT NULL,
    status       VARCHAR(20) NOT NULL
                 CHECK (status IN ('pending','accepted','declined')),
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TIMESTAMP,
    FOREIGN KEY (sender_id)   REFERENCES "user"(id),
    FOREIGN KEY (receiver_id) REFERENCES "user"(id)
);

-- ==========================
--  FRIENDS  (mutual)
-- ==========================
CREATE TABLE friend (
    user_id_1   INTEGER NOT NULL,
    user_id_2   INTEGER NOT NULL,
    since       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TIMESTAMP,
    PRIMARY KEY (user_id_1, user_id_2),
    FOREIGN KEY (user_id_1) REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id_2) REFERENCES "user"(id) ON DELETE CASCADE,
    CHECK (user_id_1 < user_id_2)   -- guarantees one row per pair
);

-- ==========================
--  DIRECT BOARD FOLLOWS
-- ==========================
CREATE TABLE follow (
    user_id     INTEGER   NOT NULL,
    board_id    INTEGER   NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TIMESTAMP,
    PRIMARY KEY (user_id, board_id),
    FOREIGN KEY (user_id)  REFERENCES "user"(id) ON DELETE CASCADE,
    FOREIGN KEY (board_id) REFERENCES board(id)  ON DELETE CASCADE
);

-- ==========================
--  FOLLOW STREAMS  (owned by user)
-- ==========================
CREATE TABLE follow_stream (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER      NOT NULL,
    stream_name   VARCHAR(120) NOT NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    terminated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Junction: boards included in a stream
CREATE TABLE follow_stream_board (
    stream_id   INTEGER   NOT NULL,
    board_id    INTEGER   NOT NULL,
    added_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  TIMESTAMP,
    PRIMARY KEY (stream_id, board_id),
    FOREIGN KEY (stream_id) REFERENCES follow_stream(id) ON DELETE CASCADE,
    FOREIGN KEY (board_id)  REFERENCES board(id)        ON DELETE CASCADE
);
