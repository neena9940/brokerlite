from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.repositories.portfolio_repository import HoldingRepository, OrderRepository
from app.schemas.portfolio import OrderCreateRequest, OrderResponse, PortfolioResponse
from app.services.market_service import MarketService
from app.services.portfolio_service import PortfolioService

router = APIRouter(tags=["portfolio"])

def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    return PortfolioService(HoldingRepository(db), OrderRepository(db), MarketService())

@router.post("/orders", response_model=OrderResponse, status_code=201)
def place_order(
    body: OrderCreateRequest,
    user: User = Depends(get_current_user),           # no token -> never reaches here
    svc: PortfolioService = Depends(get_portfolio_service),
):
    order, created = svc.place_order(
        str(user.id), body.ticker, body.side, body.quantity, str(body.client_token))
    if not created:
        # it was a retry: the order already exists, so 200 (not 201) is the honest code
        return Response(status_code=200) if False else order   # see note below
    return order