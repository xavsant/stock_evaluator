# FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

# Classes
from backend.sentiment_analysis import Stock_SentimentAnalysis
from backend.black_scholes_merton import BlackScholesMertonModel
from backend.monte_carlo import MonteCarloSimulation

# Utility
from backend.utils.data_fetching import StockData
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
    r: float = 0.02
    S: float = 10
    K: float = 15
    T: int = 548
    sigma: float = 0.2
    type_option: str = "c"

class StockSymbolsRequest(BaseModel):
    stock_symbols: List[str] = ["AAPL"]
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
        r=request.r, 
        S=request.S, 
        K=request.K, 
        T=request.T, 
        sigma=request.sigma, 
        type_option=request.type_option)
    
    return {"message": "Black Scholes Merton model initialised successfully"}

@app.post("/initialise_monte_carlo")
async def initialise_monte_carlo(request: StockSymbolsRequest):
    global monte_carlo_instance
    
    # Initialise or reinitialise the MonteCarloSimulation instance
    start_date = datetime.now() - timedelta(days=request.historical_timeframe)
    stock_data = StockData(stock_list=request.stock_symbols, start_date=start_date)
    monte_carlo_instance = MonteCarloSimulation(
        stock_data=stock_data,
        num_simulations=request.num_simulations,
        forecast_timeframe=request.forecast_timeframe
    )
    
    return {"message": "Monte Carlo simulation initialised successfully"}

# ---
# Sentiment Analysis
# ---
@app.post("/stock_sentiment_analysis")
async def stock_sentiment_analysis(stock: str) -> dict:
    try:
        app = Stock_SentimentAnalysis(stock)
        result = app.run()
        return {"success": True, "payload": result}
    except TimeoutError as e:
        return {"success": False, "error": str(e)}
    
# ---
# Black Scholes Merton Options
# ---
@app.post("/black_scholes_merton_option/greeks")
async def black_scholes_merton_option() -> dict:
    if black_scholes_merton_instance is None:
        raise HTTPException(status_code=500, detail="Black Scholes Merton model instance not initialised")
    
    try:
        greeks = black_scholes_merton_instance.greeks()
        return {"success": True, "payload": greeks}
    except TypeError as e:
        return {"success": False, "error": str(e)}

@app.post("/black_scholes_merton_option/plot")
async def black_scholes_merton_option(tr_type: str, op_pr: float):
    if black_scholes_merton_instance is None:
        raise HTTPException(status_code=500, detail="Black Scholes Merton model instance not initialised")

    img_buf = black_scholes_merton_instance.plot_option_price(tr_type, op_pr)
    return StreamingResponse(img_buf, media_type="image/png")

# ---
# Monte Carlo Simulations
# ---
@app.post("/plot_simulation_lines")
async def plot_simulation_lines():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised")
    
    plot_json = monte_carlo_instance.plot_simulation_lines(return_as_json=True)
    return plot_json

@app.post("/plot_simulation_avg")
async def plot_simulation_avg():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised")
    
    plot_json = monte_carlo_instance.plot_simulation_avg(return_as_json=True)
    return plot_json

@app.post("/plot_histogram_with_risk_metrics")
async def plot_histogram_with_risk_metrics():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised")
    
    plot_json = monte_carlo_instance.plot_histogram_with_risk_metrics(return_as_json=True)
    return plot_json

@app.post("/plot_corr_heatmap")
async def plot_corr_heatmap():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised")
    
    corr_heatmap = monte_carlo_instance.corr_heatmap()
    return StreamingResponse(corr_heatmap, media_type="image/png")

@app.post("/generate_risk_metrics")
async def generate_risk_metrics():
    if monte_carlo_instance is None:
        raise HTTPException(status_code=500, detail="Monte Carlo instance not initialised")
    
    risk_metrics_table = monte_carlo_instance.display_risk_metrics_table_with_insights()
    return StreamingResponse(risk_metrics_table, media_type="image/png")