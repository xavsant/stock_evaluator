# Imports
import streamlit as st
from backend.utils.data_fetching import Finnhub
from os import environ

# Initialise env variables
finnhub_api_key = environ["FINNHUB_API_KEY"]

# Initialize session state for tickers
if "tickers" not in st.session_state:
    st.session_state.tickers = Finnhub.get_tickers(finnhub_api_key)  # Fetch tickers once

pages = {
    "Functions": [
        st.Page("streamlit/monte_carlo_app.py", title="Monte Carlo Simulation"),
        st.Page("streamlit/black_scholes_merton_app.py", title="Black Scholes Merton"),
        st.Page("streamlit/sentiment_analysis_app.py", title="Sentiment Analysis"),
    ]
}

pg = st.navigation(pages)
pg.run()



