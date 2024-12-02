# Import utility functions
from .data_fetching import WebScraper, MonteCarlo_StockData, Black_Scholes_Merton_StockData, Finnhub

# Expose imports so they are accessible directly from `utils`
__all__ = [
    "WebScraper",
    "MonteCarlo_StockData", 
    "Black_Scholes_Merton_StockData", 
    "Finnhub"
]
