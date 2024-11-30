# Imports
import streamlit as st
from requests import post as rpost

# Plot Imports
from PIL import Image
from io import BytesIO

def black_scholes_merton_initialise_request(interest_rate: float, spot_price: float, strike_price: float, time: int, sigma: float, \
                                   option_type: str, position: str, premium: float):
     header = {"Content-Type": "application/json"}

     parameters = {
         "interest_rate": interest_rate,
         "spot_price": spot_price,
         "strike_price": strike_price,
         "time": time,
         "sigma": sigma,
         "option_type": option_type,
         "position": position,
         "premium": premium
         }

     response = rpost(
          url="http://0.0.0.0:8000/initialise_black_scholes_merton",
          headers=header,
          json=parameters
     )

     return response.json()

def black_scholes_merton_get_greeks():
    header = {"Content-Type": "application/json"}

    response = rpost(
          url="http://0.0.0.0:8000/black_scholes_merton_option/greeks",
          headers=header
     )

    return response.json()

def black_scholes_merton_plot_payoffs():
    header = {"Content-Type": "application/json"}

    response = rpost(
          url="http://0.0.0.0:8000/black_scholes_merton_option/plot",
          headers=header,
          stream=True
    )

    response_image = Image.open(BytesIO(response.content))

    return response_image

def compare_prices(theoretical_option_price: float, actual_option_price: float):
    """
    Compares the theoretical option price calculated by the Black Scholes Merton model against the actual option price (spot price + premium)
    """
    if round(theoretical_option_price, 2) > round(actual_option_price, 2):
        return 'underpriced'
    elif round(theoretical_option_price, 2) < round(actual_option_price, 2):
        return 'overpriced'
    else:
        'priced fairly'

def evaluate_option_type(option_type: str):
    if option_type == 'Call (📈)':
        return 'c'
    else:
        return 'p'
    
def evaluate_position(position: str):
    if position == 'Buy (Long)':
        return 'b'
    else:
        return 's'

def sidebar():
    st.sidebar.title("Input Variables")

    stock = st.sidebar.selectbox("Select Portfolio of Stock:", options = ['AAPL', 'TSLA', 'NVDA']) # get Current Stock Price
    interest_rate = st.sidebar.number_input("Risk Free Interest Rate:", min_value = 0.01, value=0.03)
    spot_price = st.sidebar.number_input("Spot Price:", min_value = 0) # from stock, filled up automatically
    sigma = st.sidebar.number_input("Volatility:", min_value = 0.00) # from stock, filled up automatically
    strike_price = st.sidebar.number_input("Strike Price:", min_value = 0)
    time = st.sidebar.number_input("Time to Expiration (days):", min_value = 0) # days

    option_type = st.sidebar.selectbox("Type of Option", options = ['Call (📈)', 'Put (📉)'])
    position = st.sidebar.selectbox("Type of Position", options = ['Buy (Long)', 'Sell (Short)'])
    option_type = evaluate_option_type(option_type) # evaluate to correct input
    position = evaluate_position(position)
    premium = st.sidebar.number_input("Option Premium:", min_value = 0)
    
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        black_scholes_merton_initialise_request(interest_rate, spot_price, strike_price, time, sigma, \
                                   option_type, position, premium)
        greeks = black_scholes_merton_get_greeks()
        plot_payoffs = black_scholes_merton_plot_payoffs()
        value = compare_prices(greeks["payload"]["option_price"], spot_price+premium)
        
        st.write(greeks)
        st.image(plot_payoffs)
        st.markdown(f"Theoretical Option Price: {greeks["payload"]["option_price"]}  \n  Actual Option Price: {spot_price+premium}")
        st.markdown(f"The actual option price is {value}.")

# Layout for the application
def main():
    st.header("Black Scholes Merton for Stock Options")
    st.markdown("This function uses the Black Scholes Merton model to generate key insights for a chosen stock option.  \n  \
                Select your variables in the column on the left.")
    "---"

    st.write("### Output")
    sidebar()
    
if __name__ == "__page__":
    main()


    # Imports
# import streamlit as st
# from requests import post as rpost

# # Plot Imports
# import plotly.graph_objects as go
# from json import loads
# from PIL import Image
# from io import BytesIO

# def monte_carlo_initialise_request(stock_symbols: list, num_each_stock: list, historical_timeframe: int, forecast_timeframe: int, num_simulations: int):
#      header = {"Content-Type": "application/json"}

#      parameters = {
#          "stock_symbols": stock_symbols,
#          "num_each_stock": num_each_stock,
#          "historical_timeframe": historical_timeframe,
#          "forecast_timeframe": forecast_timeframe,
#          "num_simulations": num_simulations
#          }

#      response = rpost(
#           url="http://0.0.0.0:8000/initialise_monte_carlo",
#           headers=header,
#           json=parameters
#      )

#      return response.json()

# def monte_carlo_get_key_data():
#     header = {"Content-Type": "application/json"}

#     response = rpost(
#           url="http://0.0.0.0:8000/monte_carlo/key_data",
#           headers=header
#      )

#     return response.json()

# def monte_carlo_plot_simulation_lines():
#     response = rpost(
#           url="http://0.0.0.0:8000/monte_carlo/plot_simulation_lines"
#      )

#     plot_json = response.json()
#     fig = go.Figure(loads(plot_json))

#     return fig

# def monte_carlo_plot_simulation_avg():
#     response = rpost(
#           url="http://0.0.0.0:8000/monte_carlo/plot_simulation_avg"
#      )

#     plot_json = response.json()
#     fig = go.Figure(loads(plot_json))

#     return fig

# def monte_carlo_plot_individual_cumulative_returns():
#     response = rpost(
#           url="http://0.0.0.0:8000/monte_carlo/plot_individual_cumulative_returns"
#      )

#     plot_json = response.json()
#     fig = go.Figure(loads(plot_json))

#     return fig

# def monte_carlo_plot_histogram_with_risk_metrics():
#     response = rpost(
#           url="http://0.0.0.0:8000/monte_carlo/plot_histogram_with_risk_metrics"
#      )

#     plot_json = response.json()
#     fig = go.Figure(loads(plot_json))

#     return fig

# def monte_carlo_plot_corr_heatmap():
#     header = {"Content-Type": "application/json"}

#     response = rpost(
#           url="http://0.0.0.0:8000/monte_carlo/plot_corr_heatmap",
#           headers=header,
#           stream=True
#     )

#     response_image = Image.open(BytesIO(response.content))

#     return response_image

# def monte_carlo_generate_risk_metrics():
#     header = {"Content-Type": "application/json"}

#     response = rpost(
#           url="http://0.0.0.0:8000/monte_carlo/generate_risk_metrics",
#           headers=header,
#           stream=True
#     )

#     response_image = Image.open(BytesIO(response.content))

#     return response_image

# def popover_shares(portfolio):
#     with st.sidebar.popover("Adjust shares"):
#         shares = {}
#         for stock in portfolio:
#             shares[stock] = st.number_input(
#                 f"Shares for {stock}",
#                 min_value=1,
#                 value=100,
#                 step=1,
#                 key=f"share_{stock}",
#             )

#     return shares

# def sidebar():
#     st.sidebar.title("Input Variables")

#     stock_symbols = st.sidebar.multiselect("Select Portfolio of Stock:", options = ['AAPL', 'TSLA', 'NVDA'], default = ['AAPL', 'NVDA'])
#     num_each_stock = popover_shares(stock_symbols)
#     historical_timeframe = st.sidebar.slider("Historical Range (days):", value = 365, min_value = 90, max_value = 1825)
#     forecast_timeframe = st.sidebar.slider("Forecast Range (days):", value = 30, min_value = 30, max_value = 365)
#     num_simulations = st.sidebar.slider("Number of Simulations:", value = 100, min_value = 100, max_value = 1000)

#     generate_button = st.sidebar.button("Generate")

#     if generate_button:
#         monte_carlo_initialise_request(stock_symbols, list(num_each_stock.values()), historical_timeframe, forecast_timeframe, num_simulations)
#         key_data = monte_carlo_get_key_data()
#         plot_simulation_lines = monte_carlo_plot_simulation_lines()
#         plot_simulation_avg = monte_carlo_plot_simulation_avg()
#         plot_individual_cumulative_returns = monte_carlo_plot_individual_cumulative_returns()
#         plot_histogram_with_risk_metrics = monte_carlo_plot_histogram_with_risk_metrics()
#         plot_corr_heatmap = monte_carlo_plot_corr_heatmap()
#         risk_metrics = monte_carlo_generate_risk_metrics()
#         st.write(key_data)
#         st.plotly_chart(plot_simulation_lines, use_container_width=True)
#         st.plotly_chart(plot_simulation_avg, use_container_width=True)
#         st.plotly_chart(plot_individual_cumulative_returns, use_container_width=True)
#         st.plotly_chart(plot_histogram_with_risk_metrics, use_container_width=True)
#         st.image(plot_corr_heatmap)
#         st.image(risk_metrics)
