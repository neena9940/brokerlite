from fastapi import FastAPI
from app.routers import auth, portfolio

app = FastAPI(title="BrokerLite Portfolio Service")

# Only include the routers that belong to THIS service
app.include_router(auth.router)
app.include_router(portfolio.router)