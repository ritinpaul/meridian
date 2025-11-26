import asyncio
import os

import redis.asyncio as redis


async def main() -> None:
    redis_url = os.getenv("MERIDIAN_REDIS_URL", "redis://localhost:6379/0")
    channel = os.getenv("MERIDIAN_REDIS_CHANNEL", "meridian.positions")

    client = redis.from_url(redis_url, decode_responses=True)
    pubsub = client.pubsub()
    await pubsub.subscribe(channel)

    print(f"Listening on channel '{channel}'...")
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                print(message["data"])
            await asyncio.sleep(0)
    except KeyboardInterrupt:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
