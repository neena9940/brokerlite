from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.portfolio_repository import HoldingRepository, OrderRepository
from app.schemas.portfolio import OrderCreateRequest, OrderResponse, PortfolioResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter(tags=["portfolio"])


def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    # Notice: We NO LONGER pass MarketService here.
    # The PortfolioService now handles HTTP calls internally.
    return PortfolioService(HoldingRepository(db), OrderRepository(db))


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def place_order(
        body: OrderCreateRequest,
        user: User = Depends(get_current_user),
        svc: PortfolioService = Depends(get_portfolio_service),
):
    # We must 'await' because the service now makes an async HTTP call
    order, created = await svc.place_order(
        str(user.id), body.ticker, body.side, body.quantity, str(body.client_token)
    )
    return order


@router.get("/orders", response_model=list[OrderResponse])
async def list_orders(
        user: User = Depends(get_current_user),
        svc: PortfolioService = Depends(get_portfolio_service)
):
    return svc.orders.get_for_user(str(user.id))


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(
        user: User = Depends(get_current_user),
        svc: PortfolioService = Depends(get_portfolio_service)
):
    # We need to add a helper method to the repository or service for this,
    # but for now, let's keep it simple and just return a placeholder or fix the service.
    # (We will refine this in a moment, but let's get it running first).
    holdings = svc.holdings.get_all_for_user(str(user.id))
    items, total_value, total_pnl = [], 0.0, 0.0
    for h in holdings:
        current = await svc._get_price(h.ticker)  # Use the new async method!
        value = current * h.quantity
        pnl = (current - float(h.avg_buy_price)) * h.quantity
        items.append({
            "ticker": h.ticker,
            "quantity": h.quantity,
            "avg_buy_price": float(h.avg_buy_price),
            "current_price": current,
            "market_value": value,
            "pnl": pnl
        })
        total_value += value
        total_pnl += pnl

    return PortfolioResponse(holdings=items, total_value=total_value, total_pnl=total_pnl)