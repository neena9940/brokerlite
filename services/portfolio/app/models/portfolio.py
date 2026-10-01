import uuid
from sqlalchemy import String, ForeignKey, Numeric, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Holding(Base):
    __tablename__ = "holdings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    ticker: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    avg_buy_price: Mapped[float] = mapped_column(Numeric(12, 4))  # needed to compute P&L

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        # THE idempotency guarantee: the database physically rejects duplicates.
        # Even two requests arriving at the exact same millisecond can't double-create.
        UniqueConstraint("user_id", "idempotency_key", name="uq_order_idem"),
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    ticker: Mapped[str] = mapped_column(String(10))
    side: Mapped[str] = mapped_column(String(4))          # "BUY" or "SELL"
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Numeric(12, 4))  # price at execution
    status: Mapped[str] = mapped_column(String(10), default="FILLED")
    idempotency_key: Mapped[str] = mapped_column(String(64))