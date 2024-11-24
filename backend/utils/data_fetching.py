# Web Scraping Imports
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Fetching Stock Data Imports
import numpy as np
import yfinance as yf
import datetime as dt

# Utility
import requests

class WebScraper:
    def __init__(self, stock):
        self.stock = stock
        self.url = "https://finance.yahoo.com/"
        self.driver = None
        self.stock_name = None
        self.hyperlink_list = []
        self.headline_list = []
        self.article_list = []

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(self.url)
        self.driver.maximize_window()

    def accept_cookies(self):
        consent_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='consent-page']/div/div/div/form/div[2]/div[2]/button[1]")))
        self.driver.execute_script("arguments[0].click();", consent_button)

    def search_stock(self):
        try:
            search_box = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[id="ybar-sbq"][name="p"]')))
            initial_url = self.driver.current_url
            self.driver.execute_script("arguments[0].value = arguments[1];", search_box, self.stock)
            search_box.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 5).until(lambda driver: driver.current_url != initial_url)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        except:
            raise TimeoutError("Stock name could not be found.")

    def scrape_articles(self):
        response = requests.get(self.driver.current_url)
        soup = BeautifulSoup(response.text, "lxml")
        self.stock_name = soup.find("h1", class_="yf-xxbei9").text.strip()
        self.hyperlink_list = [a["href"] for a in soup.find_all("a", class_="subtle-link fin-size-small thumb yf-1e4diqp")]
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

    def close_driver(self):
        if self.driver:
            self.driver.quit()


class StockData:
    def __init__(self, stock_list, 
                 start_date=dt.datetime.now() - dt.timedelta(days=365), 
                 end_date=dt.datetime.now(), 
                 weights=None):
        self.stocks = stock_list
        self.start = start_date
        self.end = end_date
        self.mean_returns, self.cov_matrix, self.corr_matrix = self.get_data() # re-structure

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