# Import utility functions
from .data_fetching import fetch_stock_data

# Expose imports so they are accessible directly from `utils`
__all__ = [
    "fetch_stock_data"
]
