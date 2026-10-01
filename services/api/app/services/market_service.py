import random

from app.core.redis import redis_client


class MarketService:
    CACHE_TTL_SECONDS = 30  # prices are "fresh enough" for 30s

    def __init__(self):
        # fake "real world": 10 tickers with plausible base prices
        self._base = {"AAPL": 190.0, "MSFT": 420.0, "NVDA": 880.0,
                      "AMZN": 185.0, "GOOG": 165.0, "TSLA": 250.0,
                      "META": 505.0, "JPM": 210.0, "V": 280.0, "XOM": 115.0}
        self._current = dict(self._base)

    def _tick(self, ticker: str) -> float:
        # random walk: each call nudges the price ~1% in either direction
        price = self._current[ticker]
        self._current[ticker] = max(1.0, price * (1 + random.gauss(0, 0.01)))
        return self._current[ticker]

    def get_price(self, ticker: str) -> float:
        ticker = ticker.upper()
        if ticker not in self._base:
            raise ValueError(f"Unknown ticker: {ticker}")
        return self._tick(ticker)

    def get_price_cached(self, ticker: str) -> tuple[float, str]:
        """Returns (price, cache_status) where status is 'HIT' or 'MISS'."""
        key = f"price:{ticker}"
        cached = redis_client.get(key)
        if cached is not None:
            return float(cached), "HIT"   # served from Redis, generator untouched
        price = self.get_price(ticker)    # only on MISS do we do the "work"
        redis_client.setex(key, self.CACHE_TTL_SECONDS, price)  # set WITH expiry
        return price, "MISS"

    def get_all_prices_cached(self) -> tuple[dict[str, float], str]:
        # "HIT" only if ALL tickers were cached — good enough for the demo
        prices, all_hit = {}, True
        for ticker in self._base:
            p, hit = self.get_price_cached(ticker)
            prices[ticker] = p
            all_hit = all_hit and (hit == "HIT")
        return prices, "HIT" if all_hit else "MISS"