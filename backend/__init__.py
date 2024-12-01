# Import classes
from .monte_carlo import MonteCarloSimulation
from .black_scholes_merton import BlackScholesMertonModel
from .sentiment_analysis import Stock_SentimentAnalysis

# Import utility functions
from .utils.data_fetching import WebScraper

# Expose imports so they are accessible directly from `backend`
__all__ = [
    "MonteCarloSimulation",
    "BlackScholesModel",
    "Stock_SentimentAnalysis"
    "WebScraper",
    "SentimentModel"
]
