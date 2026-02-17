from pyspark.sql import SparkSession


def create_spark(app_name: str) -> SparkSession:
    spark = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.shuffle.partitions", "1")
        .config("spark.sql.streaming.ui.enabled", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    return spark


def read_kafka_stream(spark: SparkSession, bootstrap: str, topic: str):
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", bootstrap)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .load()
    )


def main():
    spark = create_spark("RawKafkaReader")
    raw_df = read_kafka_stream(spark, "127.0.0.1:9092,127.0.0.1:19092,127.0.0.1:29092", "test-transactions")

    query = (
        raw_df
        .selectExpr("CAST(value AS STRING) AS message")
        .writeStream
        .format("console")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
