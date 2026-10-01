from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# connection pool: reuse connections instead of reconnecting per request
engine = create_engine(settings.database_url)

# autoflush=False: nothing hits the DB until you explicitly commit()
# autocommit=False: transactions are explicit (you control commit/rollback)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass                        # all models inherit from this — Alembic finds them via it

def get_db():
    db = SessionLocal()         # one session per request...
    try:
        yield db                # ...handed to the route via Depends...
    finally:
        db.close()              # ...always closed, even if the route crashes