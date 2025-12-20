import redis
import json
import time
from datetime import datetime


class RedisPublisher:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True  # Auto-decode bytes to strings
        )

    def publish(self, channel, message):
        """
        Publish a message to a channel
        Returns: number of subscribers that received the message
        """
        return self.client.publish(channel, message)

    def publish_json(self, channel, data):
        """Publish JSON-serialized data"""
        message = json.dumps(data)
        return self.publish(channel, message)

    def close(self):
        """Close the connection"""
        self.client.close()


if __name__ == "__main__":
    # Initialize publisher
    pub = RedisPublisher(host='localhost', port=6379)

    # Example 1: Publish simple string messages
    channel = "test-channel"

    print(f"Publishing to channel: {channel}")

    # Publish messages in a loop
    for i in range(100):
        # Simple message
        subscribers = pub.publish(channel, f"Message {i}")
        print(f"Published message {i} to {subscribers} subscribers")

        # JSON message with structured data
        data = {
            "speed": 12.5 + i * 0.5,
        }
        subscribers = pub.publish_json(f"{channel}:json", data)
        print(f"Published JSON data to {subscribers} subscribers")

        time.sleep(1)

    pub.close()
    print("Publisher closed")
