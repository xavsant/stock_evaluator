# Web Scraping Imports
from bs4 import BeautifulSoup

# Fetching Stock Data Imports
import numpy as np
import yfinance as yf
import datetime as dt

# Utility
import os
import requests
import pickle

# Get directory of pickled models
base_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.abspath(os.path.join(base_dir, "..", "models"))
name2ticker_path = os.path.join(utils_dir, "name2ticker_dict.pkl")

class WebScraper:
    def __init__(self, stock):
        self.stock = stock.strip().upper()
        self.url = "https://finance.yahoo.com/quote/"
        with open(name2ticker_path, "rb") as f:
            self.name2ticker_dict = pickle.load(f)
        self.stock_name = None
        self.hyperlink_list = []
        self.headline_list = []
        self.article_list = []

    def get_request(self, url_extension):
        response = requests.get(self.url + url_extension + '/')
        soup = BeautifulSoup(response.text, "lxml")
        self.stock_name = soup.find("h1", class_="yf-xxbei9").text.strip()
        self.hyperlink_list = [a["href"] for a in soup.find_all("a", class_="subtle-link fin-size-small thumb yf-1e4diqp")]

    def search_stock(self):
        try:
            self.get_request(self.stock)
        except:
            for name in self.name2ticker_dict:
                if self.stock in name:
                    self.get_request(self.name2ticker_dict[name])
                    break
        if self.stock_name == None:
            raise ValueError("Stock does not exist!")

    def scrape_articles(self):
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

class StockData:
    def __init__(self, stock_list, 
                 start_date=dt.datetime.now() - dt.timedelta(days=100), 
                 end_date=dt.datetime.now(), 
                 weights=None):
        self.stocks = stock_list
        self.start = start_date
        self.end = end_date
        self.mean_returns, self.cov_matrix, self.corr_matrix = self.get_data()

        self.stock_num = len(self.mean_returns)
        if weights is not None:
            if len(weights) != len(stock_list):
                raise ValueError("Weights do not match the number of stocks inputted.")
            self.weights = weights
        else:
            self.weights = self.set_weights()
    
    def get_data(self):
        df = yf.download(self.stocks, self.start, self.end)
        print(df)
        df_close = df["Close"]
        print(df_close)
        returns = df_close.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        corr_matrix = returns.corr()
        return mean_returns, cov_matrix, corr_matrix 
    
    def set_weights(self):
        weights = np.random.random(self.stock_num)
        weights /= np.sum(weights)
        return weights
