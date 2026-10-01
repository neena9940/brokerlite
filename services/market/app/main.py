from fastapi import FastAPI, Response, HTTPException
from app.market_service import MarketService

app = FastAPI(title="BrokerLite Market Service")

# Instantiate once at the module level
market = MarketService()


@app.get("/prices")
def get_prices(response: Response):
    prices = {}
    all_hit = True

    for ticker in market._base:
        p, hit = market.get_price(ticker)
        prices[ticker] = p
        # If even one ticker is a MISS, the whole response is a MISS
        all_hit = all_hit and (hit == "HIT")

    response.headers["X-Cache"] = "HIT" if all_hit else "MISS"
    return prices


@app.get("/prices/{ticker}")
def get_price(ticker: str, response: Response):
    try:
        price, status = market.get_price(ticker.upper())
    except KeyError:  # Fallback if ticker not in _base dict
        raise HTTPException(status_code=404, detail="Unknown ticker")

    response.headers["X-Cache"] = status
    return {"ticker": ticker.upper(), "price": price}