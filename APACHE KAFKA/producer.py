from confluent_kafka import Producer
import json
import time

# Configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'test-producer',
    'acks': 'all',
    'retries': 3,
    'linger.ms': 100,
    'compression.type': 'snappy'
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

for i in range(100):
    message = {
        'latitude': 53.5511,
        'longitude': 9.9937
    }

    # Produce message (non-blocking)
    producer.produce(
        topic=topic,
        value=json.dumps(message).encode('utf-8'),
        callback=delivery_callback
    )

    # Trigger callbacks
    producer.poll(0)

    time.sleep(1)

# Wait for all messages to be delivered
producer.flush()
