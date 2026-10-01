import random
import redis
import os


class MarketService:
    CACHE_TTL = 30  # Cache expires after 30 seconds

    def __init__(self):
        # 1. Redis connection
        self.redis = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True
        )

        # 2. Base prices and current state
        self._base = {
            "AAPL": 190.0, "MSFT": 420.0, "NVDA": 880.0,
            "AMZN": 185.0, "GOOG": 165.0, "TSLA": 250.0,
            "META": 505.0, "JPM": 210.0, "V": 280.0, "XOM": 115.0
        }
        self._current = dict(self._base)

    def _tick(self, ticker: str) -> float:
        # 3. Simulate market movement
        price = self._current[ticker]
        # Random walk: +/- 1% change, but never drop below 1.0
        self._current[ticker] = max(1.0, price * (1 + random.gauss(0, 0.01)))
        return self._current[ticker]

    def get_price(self, ticker: str) -> tuple[float, str]:
        # 4. Cache-Aside Pattern
        key = f"price:{ticker}"
        print(key)
        price = self.redis.get(key)
        cached = self.redis.get(key)

        if cached is not None:
            return float(cached), "HIT"

        # Cache miss: compute new price
        price = self._tick(ticker)

        # Save to Redis with an expiration time (TTL)
        self.redis.setex(key, self.CACHE_TTL, price)
        print(f"Stored {price} for {key}")
        return price, "MISS"