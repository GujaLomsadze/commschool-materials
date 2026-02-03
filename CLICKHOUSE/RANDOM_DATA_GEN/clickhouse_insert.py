import os
import uuid
import random
from datetime import datetime, timedelta
from multiprocessing import Process, cpu_count
from clickhouse_driver import Client

# ==============================
# CONFIG
# ==============================
CLICKHOUSE_CONFIG = {
    "host": "localhost",
    "port": 9000,
    "database": "default",
    "user": "default",
    "password": "123",
}

ROWS_PER_BATCH = 10_000      # ClickHouse likes BIG batches
BATCHES_PER_PROCESS = 100    # total rows per process = ROWS_PER_BATCH * BATCHES_PER_PROCESS

CURRENCIES = ["USD", "EUR", "GBP"]
PAYMENT_METHODS = ["card", "paypal", "apple_pay", "google_pay"]
STATUSES = ["paid", "pending", "failed", "refunded"]

# ==============================
# DATA GENERATOR
# ==============================
def generate_row(tx_id: int):
    quantity = random.randint(1, 5)
    price = round(random.uniform(5, 500), 2)
    total = round(quantity * price, 2)

    return (
        tx_id,
        uuid.uuid4(),                       # UUID is native in ClickHouse
        random.randint(1, 5_000_000),
        random.randint(1, 1_000_000),
        quantity,
        price,
        total,
        random.choice(CURRENCIES),
        random.choice(PAYMENT_METHODS),
        random.choice(STATUSES),
        datetime.utcnow() - timedelta(
            seconds=random.randint(0, 60 * 60 * 24 * 365)
        ),
    )

# ==============================
# WORKER PROCESS
# ==============================
def insert_worker(worker_id: int):
    client = Client(**CLICKHOUSE_CONFIG)

    insert_sql = """
        INSERT INTO ecommerce_transactions2 (
            transaction_id,
            order_id,
            user_id,
            product_id,
            quantity,
            price,
            total_amount,
            currency,
            payment_method,
            transaction_status,
            created_at
        ) VALUES
    """

    tx_id_base = worker_id * 10_000_000_000
    tx_id = tx_id_base

    total_inserted = 0

    for batch in range(BATCHES_PER_PROCESS):
        rows = []
        for _ in range(ROWS_PER_BATCH):
            rows.append(generate_row(tx_id))
            tx_id += 1

        client.execute(insert_sql, rows)
        total_inserted += len(rows)

        print(f"[Worker {worker_id}] Inserted {total_inserted:,} rows")

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    workers = cpu_count()
    print(f"Starting {workers} ClickHouse processes")

    processes = []
    for i in range(workers):
        p = Process(target=insert_worker, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("🔥 ClickHouse data generation complete")
