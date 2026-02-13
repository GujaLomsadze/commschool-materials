from confluent_kafka import Consumer, KafkaError
import json

conf = {
    'bootstrap.servers': '127.0.0.1:9092,127.0.0.1:19092,127.0.0.1:29092',
    'group.id': 'telemetry-processors-3',
    'auto.offset.reset': 'latest',
    'enable.auto.commit': False
}

consumer = Consumer(conf)
consumer.subscribe(['test-transactions'])

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
