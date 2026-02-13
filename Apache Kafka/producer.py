import random

from confluent_kafka import Producer
import json
import time

# Configuration
conf = {
    'bootstrap.servers': 'localhost:19092,localhost:19094,localhost:19096',
    'client.id': 'test-producer',
    'acks': 'all',
    'retries': 3,
    'linger.ms': 100,
    'compression.type': 'snappy',
}

producer = Producer(conf)


def delivery_callback(err, msg):
    """Callback for message delivery reports"""
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')


# Send messages
topic = 'vessel-telemetry'

while True:
    message = {
        'random_int': random.randint(0, 100),
    }

    producer.produce(
        topic=topic,
        value=json.dumps(message).encode('utf-8'),
        callback=delivery_callback
    )

    # Trigger callbacks
    producer.poll(0)
    producer.flush()

    time.sleep(0.5)
