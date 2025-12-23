from confluent_kafka import Consumer, KafkaError
import json

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'telemetry-processors',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

consumer = Consumer(conf)
consumer.subscribe(['vessel-telemetry'])

print("Listening for messages...")

try:
    while True:
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f'Error: {msg.error()}')
            continue

        # Process message
        data = json.loads(msg.value().decode('utf-8'))
        print(f"Processing: {data}")

        consumer.commit(asynchronous=False)

except KeyboardInterrupt:
    print("Shutting down...")
finally:
    consumer.close()