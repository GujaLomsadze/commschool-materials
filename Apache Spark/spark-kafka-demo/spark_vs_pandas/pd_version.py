import pandas as pd

data = [
    ("t1", "u1", 120.0, "EUR"),
    ("t2", "u2", 5000.0, "USD"),
    ("t3", "u1", 700.0, "EUR"),
    ("t4", "u3", 50.0, "EUR"),
    ("t5", "u2", 9000.0, "USD"),
]

df = pd.DataFrame(data, columns=["tx_id", "user_id", "amount", "currency"])

# Filter
filtered = df[df["amount"] > 500]

# Groupby
grouped = df.groupby("user_id")["amount"].sum()

# Count
count = df["currency"].value_counts()

print("======================================== FILETERED RESULTS")
print(filtered)
print("======================================== GROUPBY RESULTS")
print(grouped)
print("======================================== CNT RESULTS")
print(count)
