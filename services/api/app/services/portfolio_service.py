from fastapi import HTTPException, status
from app.repositories.portfolio_repository import HoldingRepository, OrderRepository
from app.services.market_service import MarketService

class PortfolioService:
    def __init__(self, holdings: HoldingRepository, orders: OrderRepository,
                 market: MarketService):
        self.holdings = holdings
        self.orders = orders
        self.market = market

    def place_order(self, user_id: str, ticker: str, side: str,
                    quantity: int, client_token: str):
        # ── IDEMPOTENCY: the retry path ──────────────────────────────
        # Scenario: frontend sent the request, network hiccuped, user clicked again.
        # Both requests carry the SAME client_token. First one wins; second gets
        # the original order back instead of creating a duplicate. Safe to retry forever.
        existing = self.orders.get_by_idempotency_key(user_id, client_token)
        if existing:
            return existing, False          # False = "not newly created"

        ticker = ticker.upper()
        if quantity <= 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Quantity must be positive")
        if side not in ("BUY", "SELL"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Side must be BUY or SELL")

        price = self.market.get_price(ticker)

        if side == "BUY":
            self.holdings.upsert_after_buy(user_id, ticker, quantity, price)
        else:
            holding = self.holdings.get(user_id, ticker)
            if not holding or holding.quantity < quantity:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not enough shares to sell")
            self.holdings.reduce_after_sell(user_id, ticker, quantity)

        order = self.orders.create(
            user_id=user_id, ticker=ticker, side=side,
            quantity=quantity, price=price, status="FILLED",
            idempotency_key=client_token,
        )
        self.orders.db.commit()             # single commit: order + holding change land together
        self.orders.db.refresh(order)
        return order, True