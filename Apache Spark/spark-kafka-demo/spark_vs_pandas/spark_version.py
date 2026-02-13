from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, count, avg, desc

# ---------- Create Spark ----------

spark = (
    SparkSession.builder
    .appName("BasicSparkExamples")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

# ---------- Create Sample Data ----------

data = [
    ("t1", "u1", 120.0, "EUR"),
    ("t2", "u2", 5000.0, "USD"),
    ("t3", "u1", 700.0, "EUR"),
    ("t4", "u3", 50.0, "EUR"),
    ("t5", "u2", 9000.0, "USD"),
]

columns = ["tx_id", "user_id", "amount", "currency"]

df = spark.createDataFrame(data, columns)

print("\n=== Original Data ===")
df.show()

# ---------- Filtering (like df[df["amount"] > 500]) ----------

print("\n=== Filter amount > 500 ===")
filtered_df = df.filter(col("amount") > 500)
filtered_df.show()

# ---------- Select Columns ----------

print("\n=== Select only user_id and amount ===")
df.select("user_id", "amount").show()

# ---------- GroupBy + Sum ----------

print("\n=== Sum amount per user ===")
df.groupBy("user_id") \
    .agg(_sum("amount").alias("total_amount")) \
    .show()

# ---------- GroupBy + Multiple Aggregations ----------

print("\n=== Multiple aggregations per user ===")
df.groupBy("user_id") \
    .agg(
    _sum("amount").alias("total_amount"),
    avg("amount").alias("avg_amount"),
    count("*").alias("num_transactions")
) \
    .show()

# ---------- Count occurrences (like value_counts) ----------

print("\n=== Count per currency ===")
df.groupBy("currency").count().show()

# ---------- Sort descending ----------

print("\n=== Sort by amount descending ===")
df.orderBy(desc("amount")).show()

# ---------- Collect to Pandas (small dataset only!) ----------

print("\n=== Convert to Pandas ===")
pdf = df.toPandas()
print(pdf)

spark.stop()
