import os
import uuid
import random
import time
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from multiprocessing import Process, cpu_count

# ==============================
# CONFIG
# ==============================
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "123",
}

ROWS_PER_BATCH = 10          # live inserts
SLEEP_SECONDS = 0.5          # throttle speed
WORKERS = 8

CURRENCIES = ["USD", "EUR", "GBP"]
PAYMENT_METHODS = ["card", "paypal", "apple_pay", "google_pay"]
STATUSES = ["paid", "pending", "failed", "refunded"]


from zoneinfo import ZoneInfo   # Python 3.9+

TBILISI_TZ = ZoneInfo("Asia/Tbilisi")

def generate_row():
    quantity = random.randint(1, 5)
    price = round(random.uniform(5, 500), 2)
    total = round(quantity * price, 2)

    # Generate local Tbilisi time, then convert to UTC
    local_time = datetime.now(TBILISI_TZ)
    utc_time = local_time.astimezone(ZoneInfo("UTC"))

    return (
        str(uuid.uuid4()),
        random.randint(1, 5_000_000),
        random.randint(1, 1_000_000),
        quantity,
        price,
        total,
        random.choice(CURRENCIES),
        random.choice(PAYMENT_METHODS),
        random.choice(STATUSES),
        utc_time,   # store UTC
    )


# ==============================
# WORKER PROCESS
# ==============================
def insert_worker(worker_id: int):
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO ecommerce_transactions (
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
        ) VALUES %s
    """

    total_inserted = 0

    try:
        while True:
            rows = [generate_row() for _ in range(ROWS_PER_BATCH)]
            execute_values(cur, insert_sql, rows)
            conn.commit()

            total_inserted += len(rows)
            print(f"[Worker {worker_id}] Total inserted: {total_inserted:,}")

            time.sleep(SLEEP_SECONDS)

    except KeyboardInterrupt:
        print(f"[Worker {worker_id}] Stopped")

    except Exception as e:
        conn.rollback()
        print(f"[Worker {worker_id}] ERROR:", e)

    finally:
        cur.close()
        conn.close()


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print(f"Starting {WORKERS} live workers")

    processes = []
    for i in range(WORKERS):
        p = Process(target=insert_worker, args=(i,))
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("🛑 Shutting down workers...")
