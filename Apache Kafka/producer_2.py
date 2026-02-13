import random
import uuid
from datetime import datetime, timezone
from confluent_kafka import Producer
import json
import time

# Configuration
conf = {
    'bootstrap.servers': 'localhost:19092,localhost:19094,localhost:19096',
    'client.id': 'test-producer2',
    'acks': 'all',
    'retries': 3,
    'linger.ms': 100,
    'compression.type': 'snappy',
}

producer = Producer(conf)


def delivery_callback(err, msg):
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(
            f'Message delivered to {msg.topic()} '
            f'[{msg.partition()}] at offset {msg.offset()}'
        )


topic = 'test-transactions'

currencies = ["EUR", "USD", "GBP", "CHF"]
user_pool = list(range(1, 10000))  # 10k possible users

while True:
    message = {
        "tx_id": str(uuid.uuid4()),
        "user_id": random.choice(user_pool),
        "amount": round(random.uniform(1.0, 10000.0), 2),  # realistic money
        "currency": random.choice(currencies),
        "ts": datetime.now(timezone.utc).isoformat()
    }

    producer.produce(
        topic=topic,
        value=json.dumps(message).encode("utf-8"),
        callback=delivery_callback
    )

    producer.poll(0)  # trigger delivery callbacks

    time.sleep(random.uniform(0.1, 1.0))  # non-uniform traffic
