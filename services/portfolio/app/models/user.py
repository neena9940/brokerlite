import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    # Mapped[...] + mapped_column: SQLAlchemy 2.0 typed style — your editor
    # knows the type, and typos become errors instead of runtime surprises
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))   # NEVER store plaintext
    role: Mapped[str] = mapped_column(String(20), default="trader")  # "trader" or "admin"
    