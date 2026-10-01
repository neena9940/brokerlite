from fastapi import FastAPI
from app.routers import auth, market

app = FastAPI(title="BrokerLite API")
app.include_router(auth.router)
app.include_router(market.router)