# Command line: streamlit run notebooks/finnhub_tickers.py
# More information: https://finnhub.io/dashboard

# ToDo: 
# - Add code for NASDAQ stock list from Finnhub to utils.data_fetching
# - Filter out unnecessary tickers from stock list
# - Figure out better way to represent tickers and company names on streamlit (separate into 2 options?)

# Imports
import streamlit as st
import pandas as pd
import requests
import yfinance as yf

# Helper Imports
from dotenv import load_dotenv
load_dotenv()
from os import environ

# API Call
finnhub_api_key = environ["FINNHUB_API_KEY"]

url = f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={finnhub_api_key}"
response = requests.get(url)
tickers = response.json()

# Filter for NASDAQ tickers and collect symbol and company name
nasdaq_tickers = [
    {"Symbol": ticker["symbol"], "Company Name": ticker["description"]}
    for ticker in tickers
    if ticker["mic"] == "XNAS"
]

# Sort tickers alphabetically by company name
nasdaq_tickers_sorted = sorted(nasdaq_tickers, key=lambda x: x["Symbol"])

# Convert to a DataFrame for easy display in Streamlit
df = pd.DataFrame(nasdaq_tickers_sorted)

# Create a new column for formatted options: (ticker) company_name
df["Formatted Option"] = df.apply(lambda x: f"({x['Symbol']}) {x['Company Name']}", axis=1)

def main():

    # Streamlit app
    st.title("NASDAQ: (Tickers) Company Names")

    # Multiselect widget for selecting options in the (ticker) company_name format
    selected_options = st.multiselect(
        "Select Companies:",
        options=df["Formatted Option"].tolist(),
        default=None
    )

if __name__ == "__main__":
    main()