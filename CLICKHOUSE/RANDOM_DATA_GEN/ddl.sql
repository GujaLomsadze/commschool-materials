CREATE TABLE ecommerce_transactions
(
    transaction_id     BIGSERIAL PRIMARY KEY,
    order_id           UUID           NOT NULL,
    user_id            BIGINT         NOT NULL,
    product_id         BIGINT         NOT NULL,
    quantity           INT            NOT NULL,
    price              NUMERIC(10, 2) NOT NULL,
    total_amount       NUMERIC(10, 2) NOT NULL,
    currency           CHAR(3)        NOT NULL,
    payment_method     VARCHAR(20)    NOT NULL,
    transaction_status VARCHAR(20)    NOT NULL,
    created_at         TIMESTAMPTZ    NOT NULL
);


CREATE TABLE ecommerce_transactions
(
    transaction_id     UInt64,
    order_id           UUID,
    user_id            UInt64,
    product_id         UInt64,
    quantity           UInt8,
    price              Decimal(10, 2),
    total_amount       Decimal(10, 2),
    currency           LowCardinality(String),
    payment_method     LowCardinality(String),
    transaction_status LowCardinality(String),
    created_at         DateTime
) ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, user_id)
SETTINGS index_granularity = 8192;


CREATE TABLE ecommerce_transactions2
(
    transaction_id     UInt64 CODEC(ZSTD(19)),
    order_id           UUID CODEC(ZSTD(19)),
    user_id            UInt64 CODEC(ZSTD(19)),
    product_id         UInt64 CODEC(ZSTD(19)),
    quantity           UInt8 CODEC(ZSTD(19)),
    price              Decimal(10, 2) CODEC(ZSTD(19)),
    total_amount       Decimal(10, 2) CODEC(ZSTD(19)),
    currency           LowCardinality(String) CODEC(ZSTD(19)),
    payment_method     LowCardinality(String) CODEC(ZSTD(19)),
    transaction_status LowCardinality(String) CODEC(ZSTD(19)),
    created_at         DateTime CODEC(Delta, ZSTD(19))
) ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY (created_at, user_id)
SETTINGS index_granularity = 8192;


