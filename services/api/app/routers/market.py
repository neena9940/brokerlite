from fastapi import APIRouter, Depends, Response

from app.services.market_service import MarketService

router = APIRouter(prefix="/market", tags=["market"])


def get_market_service() -> MarketService:
    return MarketService()


@router.get("/prices")
def get_prices(response: Response,
               market: MarketService = Depends(get_market_service)):
    prices, cache_status = market.get_all_prices_cached()
    response.headers["X-Cache"] = cache_status   # the proof, visible in curl/DevTools
    return prices


@router.get("/prices/{ticker}")
def get_price(ticker: str, response: Response,
              market: MarketService = Depends(get_market_service)):
    try:
        price, cache_status = market.get_price_cached(ticker.upper())
    except ValueError:
        return Response(status_code=404)
    response.headers["X-Cache"] = cache_status
    return {"ticker": ticker.upper(), "price": price}