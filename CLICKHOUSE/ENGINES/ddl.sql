-- MergeTree
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

-- POSTGRESQL
CREATE TABLE ecommerce_transactions_pg
(
    transaction_id     UInt64,
    order_id           UUID,
    user_id            UInt64,
    product_id         UInt64,
    quantity           Int32,
    price              Decimal(10, 2),
    total_amount       Decimal(10, 2),
    currency           FixedString(3),
    payment_method     String,
    transaction_status String,
    created_at         DateTime64(6, 'UTC')
) ENGINE = PostgreSQL('localhost:5432', 'postgres', 'ecommerce_transactions', 'postgres', '123');


-- Kafka
CREATE TABLE kafka_vessel_telemetry
(
    random_int UInt8
) ENGINE = Kafka
        SETTINGS
            kafka_broker_list = 'localhost:19092,localhost:19094,localhost:19096',
            kafka_topic_list = 'vessel-telemetry',
            kafka_group_name = 'clickhouse_vessel_telemetry_consumer',
            kafka_format = 'JSONEachRow',
            kafka_num_consumers = 3,
            kafka_max_block_size = 65536;


CREATE TABLE vessel_telemetry
(
    random_int  UInt8,
    ingest_time DateTime DEFAULT now()
) ENGINE = MergeTree
        ORDER BY ingest_time;


CREATE
MATERIALIZED VIEW mv_kafka_vessel_telemetry
    TO vessel_telemetry
AS
SELECT random_int
FROM kafka_vessel_telemetry;

SELECT *
FROM system.kafka_consumers;

SELECT *
FROM mv_kafka_vessel_telemetry;
