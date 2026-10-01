import redis
import os
import time

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
# 1. Add socket_timeout=10.0 (longer than the 5s block time)
r = redis.Redis.from_url(redis_url, decode_responses=True, socket_timeout=10.0)

STREAM_NAME = "order-events"
GROUP_NAME = "notifiers"
CONSUMER_NAME = "consumer-1"

# 2. Create the consumer group if it doesn't exist
try:
    r.xgroup_create(STREAM_NAME, GROUP_NAME, id="$", mkstream=True)
except redis.ResponseError:
    pass  # Group already exists

print(f"🔔 Notification service listening on stream '{STREAM_NAME}'...")

# 3. The infinite loop
while True:
    try:
        # Read messages (block for 5000ms = 5 seconds)
        resp = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME: ">"}, count=1, block=5000)

        # Process messages if we got any
        if resp:
            for stream_name, messages in resp:
                for msg_id, fields in messages:
                    print(f"📧 [NOTIFY] Sending email for Order {fields['order_id']}: "
                          f"{fields['quantity']} {fields['ticker']} @ ${fields['price']}")

                    # Acknowledge the message
                    r.xack(STREAM_NAME, GROUP_NAME, msg_id)

    except redis.exceptions.TimeoutError:
        # If it times out, just loop back and try again
        print("⏳ Redis timeout, retrying...")
        continue
    except redis.exceptions.ConnectionError:
        # If the connection drops, wait a bit and reconnect
        print("🔌 Redis connection lost, retrying in 5 seconds...")
        time.sleep(5)
        continue