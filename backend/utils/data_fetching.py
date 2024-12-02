# Web Scraping Imports
from bs4 import BeautifulSoup

# Fetching Stock Data
import yfinance as yf
import datetime as dt
import requests

# Utility
from typing import List, Optional
import os
import requests
import pickle
from dotenv import load_dotenv
load_dotenv()

# Get directory of pickled models
base_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.abspath(os.path.join(base_dir, "..", "models"))
name2ticker_path = os.path.join(utils_dir, "name2ticker_dict.pkl")

class WebScraper:
    """
    Scrapes Yahoo Finance for relevant articles for a given stock.

    Inputs:
        stock (str): stock (str): Ticker or company name of a stock. If company name is provided, it references a pre-scraped dictionary from https://stockanalysis.com/stocks/ to determine the ticker value. As companies may drop in and out of the stock list, utilise ticker for best results.
    
    Methods:
        search_stock: Searches for the provided stock.
        get_request: Utilises BeautifulSoup package to get list of hyperlinks to relevant articles for a given stock.
        scrape_articles: Scrapes the hyperlinks provided from .get_request()
    """
    def __init__(self, stock: str):
        self.stock = stock.strip().upper()
        self.url = "https://finance.yahoo.com/quote/"
        with open(name2ticker_path, "rb") as f:
            self.name2ticker_dict = pickle.load(f)
        self.stock_name = None
        self.hyperlink_list = []
        self.headline_list = []
        self.article_list = []

    def search_stock(self) -> None:
        try:
            self.get_request(self.stock)
        except:
            for name in self.name2ticker_dict:
                if self.stock in name:
                    self.get_request(self.name2ticker_dict[name])
                    break
        if self.stock_name == None:
            raise ValueError("Stock does not exist!")
        
    def get_request(self, url_extension: str) -> None:
        response = requests.get(self.url + url_extension + '/')
        soup = BeautifulSoup(response.text, "lxml")
        self.stock_name = soup.find("h1", class_="yf-xxbei9").text.strip()
        self.hyperlink_list = [a["href"] for a in soup.find_all("a", class_="subtle-link fin-size-small thumb yf-1e4diqp")]

    def scrape_articles(self) -> None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        for hyperlink in self.hyperlink_list.copy():
            try:
                article = [] # each element in this list is a different paragraph
                response = requests.get(hyperlink, headers=headers)
                soup = BeautifulSoup(response.text, "lxml")
                headline = soup.find("h1", class_="cover-title yf-1o1tx8g") # works for most yahoo finance articles
                headline = headline.text.strip() if headline else None # returns None if the mainstream case above fails
                if not headline: # special case for some yahoo tech articles where "Yahoo Tech" is the first h1 headline
                    headline = next((h.text.strip() for h in soup.find_all("h1") if not h.text.strip().startswith("Yahoo")), None) # create an iterator object and return the first element that does not start with "Yahoo"
                if headline:
                    article.append(headline if headline[-1] in ".?!" else headline + ".")
                for paragraph in soup.find_all("p"):
                    paragraph = paragraph.text.strip()
                    if paragraph:
                        article.append(paragraph if paragraph[-1] in ".?!" else paragraph + ".")
                self.headline_list.append(headline)
                self.article_list.append(" ".join(article)) # use the join method to join all the separated header and paragraphs into one long string
            except: # for cases where an article is locked behind a paywall or diverts the user to another news website
                self.hyperlink_list.remove(hyperlink)

class MonteCarlo_StockData:
    """
    Obtains relevant stock data for Monte Carlo simulations.

    Inputs:
        stock_list (List[str]): List of stocks that make up a portfolio.
        start_date (datetime): Historical start of time series for chosen stocks.
        end_date (datetime): Historical end of time series for chosen stocks, defaults to now.
        num_each_stock (List[int]|None): The shares of each stock. If None, defaults to 100.
    
    Methods:
        get_key_data: Returns key financial information.
    """
    def __init__(self, stock_list: List[str], 
                 start_date: dt.datetime = dt.datetime.now() - dt.timedelta(days=365), 
                 end_date: dt.datetime = dt.datetime.now(), 
                 num_each_stock: Optional[List[int]] = None):
        self.stocks = stock_list
        self.start = start_date
        self.end = end_date

        self.mean_price, self.mean_returns, self.cov_matrix, self.corr_matrix = self._fetch_data()
        self.stock_len = len(self.mean_returns)

        # Default to 100 shares per stock if num_each_stock not provided
        if num_each_stock is not None:
            if len(num_each_stock) != len(stock_list):
                raise ValueError("Length of numbers provided does not match number of stocks in portfolio.")
            self.num_each_stock = num_each_stock
        else:
            self.num_each_stock = [100] * self.stock_len

        self.values, self.weights = self._find_weights()
        self.port_value = sum(self.values)

    def get_key_data(self) -> dict:
        output = {
            "stock": self.stocks,
            "mean_price_per_stock": self.mean_price,
            "mean_return_per_stock": self.mean_returns,
            "shares_per_stock": self.num_each_stock,
            "value_per_stock": self.values,
            "portfolio_weight": self.weights,
            "portfolio_value": self.port_value
        }

        return output

    def _fetch_data(self) -> tuple:
        df = yf.download(self.stocks, self.start, self.end)
        # print(df)
        df_close = df["Close"]
        # print(df_close)
        mean_price = df_close.mean()
        returns = df_close.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        corr_matrix = returns.corr()
        return list(mean_price), list(mean_returns), cov_matrix, corr_matrix 

    # Based on shares and each stocks' mean price
    def _find_weights(self) -> tuple:
        values = [num * value for num, value in zip(self.num_each_stock, self.mean_price)]
        weights = [value / sum(values) for value in values] 
        return values, weights

class Black_Scholes_Merton_StockData:
    """
    Obtains relevant stock data for Black Scholes Merton model.

    Inputs:
        ticker (str): Ticker of a chosen stock.
    
    Methods:
        get_spot_and_volatility: Calculates and returns the current spot and volatility of a chosen stock. Volatility period can be changed through period ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd" (year to date -> from start of current year) "max"].
    """
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)

    def _get_spot_price(self) -> float:
        """Fetches the current spot price of the stock."""
        try:
            data = self.stock.history(period="1d")
            spot_price = data['Close'].iloc[-1]  # Get the latest closing price
            return spot_price
        except Exception as e:
            raise ValueError(f"Error retrieving spot price for {self.ticker}: {e}")

    def _get_volatility(self, period="6mo") -> float:
        """Calculates annualised volatility based on historical price data."""
        try:
            data = self.stock.history(period=period)
            daily_returns = data['Close'].pct_change().dropna()
            daily_volatility = daily_returns.std()
            annualized_volatility = daily_volatility * (126 ** 0.5)
            return annualized_volatility
        except Exception as e:
            raise ValueError(f"Error retrieving volatility for {self.ticker}: {e}")

    def get_spot_and_volatility(self, period="6mo") -> dict:
        """Returns both spot price and volatility."""
        spot_price = self._get_spot_price()
        volatility = self._get_volatility(period)
        return {"spot_price": spot_price, "volatility": volatility}

class Finnhub:
    """
    Static method to obtain tickers using Finnhub API. Uses tickers from NASDAQ.

    Inputs:
        api_key (str): Access key for Finnhub
    
    Methods:
        get_tickers: Retrieves and returns a sorted list of tickers.
    """
    @staticmethod
    def get_tickers(api_key: str) -> List[str]:
        url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={api_key}"
        response = requests.get(url)
        tickers = response.json()

        # Filter for NASDAQ tickers and collect symbol and company name
        nasdaq_tickers = [
            ticker["symbol"]
            for ticker in tickers
            if ticker["mic"] == "XNAS"
        ]

        nasdaq_tickers_sorted = sorted(nasdaq_tickers)
        return nasdaq_tickers_sorted
