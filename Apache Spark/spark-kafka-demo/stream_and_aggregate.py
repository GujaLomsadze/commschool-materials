from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, window, sum as _sum
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = (
    SparkSession.builder
    .appName("KafkaStructuredStreamingDemo")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

# Updated schema (same fields, but ts is ISO string with timezone)
schema = StructType([
    StructField("tx_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("ts", StringType(), True),
])

kafka_bootstrap = "127.0.0.1:9092,127.0.0.1:19092,127.0.0.1:29092"
topic = "test-transactions"

raw = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", kafka_bootstrap)
    .option("subscribe", topic)
    .option("startingOffsets", "latest")
    .load()
)

# Parse JSON
parsed = (
    raw.selectExpr("CAST(value AS STRING) AS json_str")
    .select(from_json(col("json_str"), schema).alias("data"))
    .select("data.*")
)

# Spark can parse ISO 8601 automatically
parsed = parsed.withColumn(
    "event_time",
    to_timestamp(col("ts"))
)

# Example: 1-minute aggregation per user
agg = (
    parsed
    .withWatermark("event_time", "2 minutes")
    .groupBy(
        window(col("event_time"), "1 minute"),
        col("user_id")
    )
    .agg(_sum("amount").alias("total_amount"))
    .selectExpr(
        "window.start as window_start",
        "window.end as window_end",
        "user_id",
        "total_amount"
    )
)

query = (
    agg.writeStream
    .format("console")
    .outputMode("update")
    .option("truncate", "false")
    .option("checkpointLocation", "/tmp/spark-kafka-checkpoints/test-transactions")
    .start()
)

query.awaitTermination()
