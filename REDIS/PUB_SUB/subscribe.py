import redis
import json
import signal
import sys


class RedisSubscriber:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        """Initialize Redis subscriber connection"""
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
        self.pubsub = self.client.pubsub()
        self.running = True

    def subscribe(self, *channels):
        """Subscribe to one or more channels"""
        self.pubsub.subscribe(*channels)
        print(f"Subscribed to channels: {channels}")

    def psubscribe(self, *patterns):
        """Subscribe to channel patterns (wildcards)"""
        self.pubsub.psubscribe(*patterns)
        print(f"Subscribed to patterns: {patterns}")

    def unsubscribe(self, *channels):
        """Unsubscribe from channels"""
        self.pubsub.unsubscribe(*channels)

    def punsubscribe(self, *patterns):
        """Unsubscribe from patterns"""
        self.pubsub.punsubscribe(*patterns)

    def listen(self, message_handler=None):
        """
        Listen for messages (blocking)
        message_handler: optional callback function(message_dict)
        """
        print("Listening for messages... (Ctrl+C to stop)")

        try:
            for message in self.pubsub.listen():
                if not self.running:
                    break

                # Skip subscription confirmation messages
                if message['type'] in ['subscribe', 'psubscribe']:
                    print(f"✓ Confirmed subscription to: {message['channel']}")
                    continue
                elif message['type'] in ['unsubscribe', 'punsubscribe']:
                    print(f"✗ Unsubscribed from: {message['channel']}")
                    continue

                # Process actual messages
                if message['type'] == 'message':
                    if message_handler:
                        message_handler(message)
                    else:
                        self._default_handler(message)

                elif message['type'] == 'pmessage':  # Pattern match
                    if message_handler:
                        message_handler(message)
                    else:
                        self._default_handler(message)

        except KeyboardInterrupt:
            print("\nStopping subscriber...")
            self.stop()

    def _default_handler(self, message):
        """Default message handler"""
        channel = message.get('channel', message.get('pattern', 'unknown'))
        data = message['data']

        # Try to parse JSON
        try:
            parsed_data = json.loads(data)
            print(f"\n[{channel}] JSON: {json.dumps(parsed_data, indent=2)}")
        except (json.JSONDecodeError, TypeError):
            print(f"\n[{channel}] {data}")

    def stop(self):
        """Stop listening"""
        self.running = False
        self.pubsub.close()
        self.client.close()
        print("Subscriber closed")


def custom_message_handler(message):
    """Example custom message handler"""
    channel = message.get('channel', message.get('pattern', 'unknown'))
    data = message['data']

    print(f"\n{'=' * 50}")
    print(f"Channel: {channel}")
    print(f"Type: {message['type']}")
    print(f"Data: {data}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    # Initialize subscriber
    sub = RedisSubscriber(host='localhost', port=6379)


    # Setup graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sub.stop()
        sys.exit(0)


    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Example 1: Subscribe to specific channels
    sub.subscribe("test-channel", "test-channel:json")

    # Example 2: Subscribe to pattern (all channels starting with "ship_")
    # sub.psubscribe("ship_*")

    # Example 3: Subscribe with custom handler
    # sub.listen(message_handler=custom_message_handler)

    # Start listening (blocking)
    sub.listen()