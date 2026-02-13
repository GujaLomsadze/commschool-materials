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


def process_batch(df, batch_id):
    print(f"\n==== Processing Batch {batch_id} ====")

    # Convert Spark DF → Pandas DF
    pdf = df.toPandas()

    if pdf.empty:
        print("No data in this batch")
        return

    print("Pandas DataFrame:")
    print(pdf.head())

    # Example Pandas operation
    print("\nTotal rows in batch:", len(pdf))


def main():
    spark = create_spark("StreamToPandas")

    raw_df = read_kafka_stream(
        spark,
        "127.0.0.1:9092,127.0.0.1:19092,127.0.0.1:29092",
        "test-transactions"
    )

    value_df = raw_df.selectExpr("CAST(value AS STRING) AS message")

    query = (
        value_df.writeStream
        .foreachBatch(process_batch)
        .outputMode("append")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
