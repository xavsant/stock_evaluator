# Imports
import streamlit as st
from requests import post as rpost

# Plot Imports
import plotly.graph_objects as go
from json import loads
from PIL import Image
from io import BytesIO

def get_tickers():
    if "tickers" in st.session_state:
        return st.session_state.tickers
    else:
        st.warning("No tickers initialized. Please restart the app.")

def monte_carlo_initialise_request(stock_symbols: list, num_each_stock: list, historical_timeframe: int, forecast_timeframe: int, num_simulations: int):
     header = {"Content-Type": "application/json"}

     parameters = {
         "stock_symbols": stock_symbols,
         "num_each_stock": num_each_stock,
         "historical_timeframe": historical_timeframe,
         "forecast_timeframe": forecast_timeframe,
         "num_simulations": num_simulations
         }

     response = rpost(
          url="http://0.0.0.0:8000/initialise_monte_carlo",
          headers=header,
          json=parameters
     )

     return response.json()

def monte_carlo_get_key_data():
    header = {"Content-Type": "application/json"}

    response = rpost(
          url="http://0.0.0.0:8000/monte_carlo/key_data",
          headers=header
     )

    return response.json()

def monte_carlo_plot_simulation_lines():
    response = rpost(
          url="http://0.0.0.0:8000/monte_carlo/plot_simulation_lines"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_simulation_avg():
    response = rpost(
          url="http://0.0.0.0:8000/monte_carlo/plot_simulation_avg"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_individual_cumulative_returns():
    response = rpost(
          url="http://0.0.0.0:8000/monte_carlo/plot_individual_cumulative_returns"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_histogram_with_risk_metrics():
    response = rpost(
          url="http://0.0.0.0:8000/monte_carlo/plot_histogram_with_risk_metrics"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_corr_heatmap():
    header = {"Content-Type": "application/json"}

    response = rpost(
          url="http://0.0.0.0:8000/monte_carlo/plot_corr_heatmap",
          headers=header,
          stream=True
    )

    response_image = Image.open(BytesIO(response.content))

    return response_image

def monte_carlo_generate_risk_metrics():
    header = {"Content-Type": "application/json"}

    response = rpost(
          url="http://0.0.0.0:8000/monte_carlo/generate_risk_metrics",
          headers=header,
          stream=True
    )

    response_image = Image.open(BytesIO(response.content))

    return response_image

def popover_shares(portfolio):
    with st.sidebar.popover("Adjust shares"):
        shares = {}
        for stock in portfolio:
            shares[stock] = st.number_input(
                f"Shares for {stock}",
                min_value=1,
                value=100,
                step=1,
                key=f"share_{stock}",
            )

    return shares

def sidebar():
    st.sidebar.title("Input Variables")

    stock_symbols = st.sidebar.multiselect("Select Portfolio of Stock:", options = get_tickers(), default = ['AAPL', 'AMZN', 'MSFT', 'NVDA', 'TSLA'])
    num_each_stock = popover_shares(stock_symbols)
    historical_timeframe = st.sidebar.slider("Historical Range (days):", value = 365, min_value = 90, max_value = 1825)
    forecast_timeframe = st.sidebar.slider("Forecast Range (days):", value = 30, min_value = 30, max_value = 365)
    num_simulations = st.sidebar.slider("Number of Simulations:", value = 100, min_value = 100, max_value = 1000)

    generate_button = st.sidebar.button("Generate")

    if generate_button:
        monte_carlo_initialise_request(stock_symbols, list(num_each_stock.values()), historical_timeframe, forecast_timeframe, num_simulations)
        key_data = monte_carlo_get_key_data()
        plot_simulation_lines = monte_carlo_plot_simulation_lines()
        plot_simulation_avg = monte_carlo_plot_simulation_avg()
        plot_individual_cumulative_returns = monte_carlo_plot_individual_cumulative_returns()
        plot_histogram_with_risk_metrics = monte_carlo_plot_histogram_with_risk_metrics()
        plot_corr_heatmap = monte_carlo_plot_corr_heatmap()
        risk_metrics = monte_carlo_generate_risk_metrics()

        st.markdown("**Portfolio Summary**")
        portfolio_value = key_data.pop("portfolio_value")
        st.dataframe(key_data, use_container_width = True)
        st.caption(f"The initial value of your portfolio is {round(portfolio_value, 4)}.")

        st.markdown("**Stock Correlation Matrix**")
        st.image(plot_corr_heatmap)
        st.plotly_chart(plot_simulation_lines, use_container_width=True)
        st.plotly_chart(plot_simulation_avg, use_container_width=True)
        st.plotly_chart(plot_individual_cumulative_returns, use_container_width=True)
        st.plotly_chart(plot_histogram_with_risk_metrics, use_container_width=True)
        st.image(risk_metrics)
        
# Layout for the application
def main():
    st.header("Monte Carlo Simulation")
    st.markdown("This function generates results for a Monte Carlo Simulation of a chosen portfolio of stock.")
    st.caption("Select your variables in the column on the left.")
    "---"

    st.write("##### Output")
    sidebar()
    
if __name__ == "__page__":
    main()