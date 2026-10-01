import redis
import httpx
from fastapi import HTTPException, status
from app.core.config import settings
from app.repositories.portfolio_repository import HoldingRepository, OrderRepository

class PortfolioService:
    def __init__(self, holdings: HoldingRepository, orders: OrderRepository):
        self.holdings = holdings
        self.orders = orders
        # Create a shared async HTTP client to talk to the Market Service
        self._market = httpx.AsyncClient(base_url=settings.market_service_url, timeout=5.0)

        self._redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    async def _get_price(self, ticker: str) -> float:
        resp = await self._market.get(f"/prices/{ticker}")
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Market service unavailable")
        return resp.json()["price"]

    async def place_order(self, user_id: str, ticker: str, side: str, quantity: int, client_token: str):
        # 1. Idempotency check
        existing = self.orders.get_by_idempotency_key(user_id, client_token)
        if existing:
            return existing, False

        ticker = ticker.upper()
        if quantity <= 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Quantity must be positive")
        if side not in ("BUY", "SELL"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Side must be BUY or SELL")

        # 2. ASYNC call to the Market Service!
        price = await self._get_price(ticker)

        # 3. Business logic
        if side == "BUY":
            self.holdings.upsert_after_buy(user_id, ticker, quantity, price)
        else:
            holding = self.holdings.get(user_id, ticker)
            if not holding or holding.quantity < quantity:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not enough shares to sell")
            self.holdings.reduce_after_sell(user_id, ticker, quantity)

        # 4. Create order and commit
        order = self.orders.create(
            user_id=user_id, ticker=ticker, side=side,
            quantity=quantity, price=price, status="FILLED",
            idempotency_key=client_token,
        )
        self.orders.db.commit()
        self.orders.db.refresh(order)

        self._publish_order_filled(order)

        return order, True

    def _publish_order_filled(self, order) -> None:
        # Redis streams require all values to be strings.
        self._redis.xadd("order-events", {
            "type": "order.filled",
            "order_id": str(order.id),
            "user_id": str(order.user_id),
            "ticker": order.ticker,
            "quantity": str(order.quantity),
            "price": str(order.price),
        })