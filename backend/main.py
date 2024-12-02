# FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Classes
from backend.sentiment_analysis import Stock_SentimentAnalysis
from backend.black_scholes_merton import BlackScholesMertonModel
from backend.monte_carlo import MonteCarloSimulation

# Utility
from backend.utils.data_fetching import MonteCarlo_StockData
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

app = FastAPI(
    title="stock evaluator service",
    summary="functions for stock evaluator web application",
    version="0.2",
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], #origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store instance
black_scholes_merton_instance = None
monte_carlo_instance = None

class BlackScholesMertonRequest(BaseModel):
    interest_rate: float = 0.02
    spot_price: float = 90.83
    strike_price: float = 85.0
    time: int = 441
    sigma: float = 0.2046
    option_type: str = "c"
    position: str = "b"
    premium: float = 12.5

class StockSymbolsRequest(BaseModel):
    stock_symbols: List[str] = ["AAPL", "TSLA", "AMZN"]
    num_each_stock: List[int] = [20, 30, 50]
    historical_timeframe: int = 365
    forecast_timeframe: int = 30
    num_simulations: int = 100

@app.on_event("startup")
async def startup_event():
    global black_scholes_merton_instance
    global monte_carlo_instance
    
# ------------
# POSTs
# ------------
@app.post("/")
async def root():
    return {"message": "no operation performed"}

@app.post("/initialise_black_scholes_merton")
async def initialise_black_scholes_merton(request: BlackScholesMertonRequest):
    global black_scholes_merton_instance
    
    black_scholes_merton_instance = BlackScholesMertonModel(
        risk_free_interest_rate=request.interest_rate, 
        spot_price=request.spot_price, 
        strike_price=request.strike_price, 
        time=request.time, 
        sigma=request.sigma, 
        premium=request.premium,
        position=request.position,
        option_type=request.option_type
        )
    
    return {"message": "Black Scholes Merton model initialised successfully."}

@app.post("/initialise_monte_carlo")
async def initialise_monte_carlo(request: StockSymbolsRequest):
    global monte_carlo_instance
    
    # Initialise or reinitialise the MonteCarloSimulation instance
    start_date = datetime.now() - timedelta(days=request.historical_timeframe)
    stock_data = MonteCarlo_StockData(stock_list=request.stock_symbols, start_date=start_date, num_each_stock=request.num_each_stock)
    monte_carlo_instance = MonteCarloSimulation(
        stock_data=stock_data,
        num_simulations=request.num_simulations,
        forecast_timeframe=request.forecast_timeframe
    )
    
    return {"message": "Monte Carlo simulation initialised successfully."}

# ---
# Sentiment Analysis
# ---
@app.post("/stock_sentiment_analysis")
async def stock_sentiment_analysis(stock: str) -> dict:
    try:
        app = Stock_SentimentAnalysis(stock)
        result = app.run()
        return {"success": True, "payload": result}
    except TimeoutError:
        return {"success": False, "error": "TimeoutError"}
    except ValueError as e:
        return {"success": False, "error": str(e)}
    
# ---
# Black Scholes Merton Options
# ---
@app.post("/black_scholes_merton_option/get_greeks")
async def black_scholes_merton_option() -> dict:
    if black_scholes_merton_instance is None:
        raise HTTPException(status_code=500, detail="Black Scholes Merton model instance not initialised.")
    
    try:
        greeks = black_scholes_merton_instance.greeks()
        return {"success": True, "payload": greeks}
    except TypeError as e:
        return {"success": False, "error": str(e)}

@app.post("/black_scholes_merton_option/plot_payoff")
async def black_scholes_merton_option():
    if black_scholes_merton_instance is None:
        raise HTTPException(status_code=500, detail="Black Scholes Merton model instance not initialised.")

    img_buf = black_scholes_merton_instance.plot_payoff()
    return StreamingResponse(img_buf, media_type="image/png")

# ---
# Monte Carlo Simulations
# ---
@app.post("/monte_carlo/key_data")
async def get_key_data():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    key_data = monte_carlo_instance.get_key_data()
    return key_data

@app.post("/monte_carlo/plot_simulation_lines")
async def plot_simulation_lines():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    plot_json = monte_carlo_instance.plot_simulation_lines(return_as_json=True)
    return plot_json

@app.post("/monte_carlo/plot_simulation_avg")
async def plot_simulation_avg():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    plot_json = monte_carlo_instance.plot_simulation_avg(return_as_json=True)
    return plot_json

@app.post("/monte_carlo/plot_individual_prices")
async def plot_individual_prices():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    plot_json = monte_carlo_instance.plot_individual_prices(return_as_json=True)
    return plot_json

@app.post("/monte_carlo/plot_individual_cumulative_returns")
async def plot_individual_cumulative_returns():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    plot_json = monte_carlo_instance.plot_individual_cumulative_returns(return_as_json=True)
    return plot_json

@app.post("/monte_carlo/plot_histogram_with_risk_metrics")
async def plot_histogram_with_risk_metrics():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    plot_json = monte_carlo_instance.plot_histogram_with_risk_metrics(return_as_json=True)
    return plot_json

@app.post("/monte_carlo/plot_corr_heatmap")
async def plot_corr_heatmap():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    corr_heatmap = monte_carlo_instance.corr_heatmap()
    return StreamingResponse(corr_heatmap, media_type="image/png")

@app.post("/monte_carlo/generate_risk_metrics")
async def generate_risk_metrics():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised.")
    
    risk_metrics_table = monte_carlo_instance.display_risk_metrics_table_with_insights()
    return StreamingResponse(risk_metrics_table, media_type="image/png")