# Import classes
from .monte_carlo import MonteCarloSimulation
from .black_scholes_merton import BlackScholesMertonModel
from .sentiment_analysis import SentimentAnalysis, Stock_SentimentAnalysis

# Import utility functions
from .utils.data_fetching import WebScraper, MonteCarlo_StockData, Black_Scholes_Merton_StockData, Finnhub

# Expose imports so they are accessible directly from `backend`
__all__ = [
    "MonteCarloSimulation",
    "BlackScholesMertonModel",
    "SentimentAnalysis",
    "Stock_SentimentAnalysis",
    "WebScraper",
    "MonteCarlo_StockData", 
    "Black_Scholes_Merton_StockData", 
    "Finnhub"
]
