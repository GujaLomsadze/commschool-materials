CREATE TABLE page_views_summing
(
    event_date Date,
    page_id    UInt32,
    views      UInt64
) ENGINE = SummingMergeTree
        ORDER BY (event_date, page_id);

INSERT INTO page_views_summing
VALUES ('2025-01-01', 1, 10),
       ('2025-01-01', 1, 5),
       ('2025-01-01', 2, 7),
       ('2025-01-01', 2, 3);


-- =================================================================================
CREATE TABLE user_profile
(
    user_id UInt32,
    name    String,
    email   String,
    version UInt32
) ENGINE = ReplacingMergeTree(version)
        ORDER BY user_id;


INSERT INTO user_profile
VALUES (1, 'Alice', 'alice@old.com', 1),
       (1, 'Alice', 'alice@new.com', 2),
       (2, 'Bob', 'bob@mail.com', 1);

SELECT *
FROM user_profile;
