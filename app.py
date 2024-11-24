# Imports
import streamlit as st

# Mock backend function
def backend_function(page, variable):
    return f"Data fetched for {page} with variable: {variable}"

pages = {
    "Functions": [
        st.Page("streamlit/monte_carlo_app.py", title="Monte Carlo Simulation"),
        st.Page("streamlit/black_scholes_merton_app.py", title="Black Scholes Merton"),
        st.Page("streamlit/sentiment_analysis_app.py", title="Sentiment Analysis"),
    ]
}

pg = st.navigation(pages)
pg.run()



