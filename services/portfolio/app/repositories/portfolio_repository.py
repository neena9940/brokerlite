from sqlalchemy.orm import Session
from app.models.portfolio import Holding, Order

class HoldingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: str, ticker: str) -> Holding | None:
        return (self.db.query(Holding)
                .filter_by(user_id=user_id, ticker=ticker).first())

    def upsert_after_buy(self, user_id: str, ticker: str, qty: int, price: float) -> None:
        holding = self.get(user_id, ticker)
        if holding:
            # weighted average: old shares at old avg + new shares at new price
            total_cost = holding.quantity * float(holding.avg_buy_price) + qty * price
            holding.quantity += qty
            holding.avg_buy_price = total_cost / holding.quantity
        else:
            self.db.add(Holding(user_id=user_id, ticker=ticker,
                                quantity=qty, avg_buy_price=price))

    def reduce_after_sell(self, user_id: str, ticker: str, qty: int) -> None:
        holding = self.get(user_id, ticker)
        holding.quantity -= qty          # sell validation happens in the service layer

    def get_all_for_user(self, user_id: str) -> list:
        return (self.db.query(Holding)
                .filter_by(user_id=user_id)
                .all())

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_idempotency_key(self, user_id: str, key: str) -> Order | None:
        return (self.db.query(Order)
                .filter_by(user_id=user_id, idempotency_key=key).first())

    def get_for_user(self, user_id: str) -> list[Order]:
        return (self.db.query(Order)
                .filter_by(user_id=user_id)
                .order_by(Order.id.desc()).limit(50).all())

    def create(self, **kwargs) -> Order:
        order = Order(**kwargs)
        self.db.add(order)
        return order                       # NOT committed here — the service owns the transaction