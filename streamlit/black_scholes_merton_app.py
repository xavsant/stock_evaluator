# Imports
import streamlit as st
from requests import post as rpost
from backend.utils.data_fetching import Black_Scholes_Merton_StockData

# Plot Imports
from PIL import Image
from io import BytesIO

def get_tickers():
    if "tickers" in st.session_state:
        return st.session_state.tickers
    else:
        st.warning("No tickers initialized. Please restart the app.")

def stock_spot_and_volatility():
    stock = st.sidebar.selectbox("Select Stock Option:", options = get_tickers(), index = 9)
    options = ["1mo", "3mo", "6mo", "1y"]
    
    selection = st.sidebar.segmented_control(
    "Historical Volatility Range", options, selection_mode="single", default = "6mo")

    stock_data = Black_Scholes_Merton_StockData(ticker = stock)
    stock_spot_and_volatility = stock_data.get_spot_and_volatility(period = selection)

    return stock_spot_and_volatility

def black_scholes_merton_initialise_request(interest_rate: float, spot_price: float, strike_price: float, time: int, sigma: float, \
                                   premium: float, position: str, option_type: str):
     header = {"Content-Type": "application/json"}

     parameters = {
         "interest_rate": interest_rate,
         "spot_price": spot_price,
         "strike_price": strike_price,
         "time": time,
         "sigma": sigma,
         "premium": premium,
         "position": position,
         "option_type": option_type
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
          url="http://0.0.0.0:8000/black_scholes_merton_option/get_greeks",
          headers=header
     )

    return response.json()

def black_scholes_merton_plot_payoff():
    header = {"Content-Type": "application/json"}

    response = rpost(
          url="http://0.0.0.0:8000/black_scholes_merton_option/plot_payoff",
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
        return 'call'
    else:
        return 'put'
    
def evaluate_position(position: str):
    if position == 'Buy (Long)':
        return 'long'
    else:
        return 'short'

def sidebar():
    st.sidebar.title("Input Variables")

    stock_data = stock_spot_and_volatility()
    spot_price = st.sidebar.number_input("Spot Price:", min_value = 0.0, value = stock_data["spot_price"])
    sigma = st.sidebar.number_input("Volatility:", min_value = 0.0, value = stock_data["volatility"])

    strike_price = st.sidebar.number_input("Strike Price:", min_value = 0.0, value = stock_data["spot_price"])
    time = st.sidebar.number_input("Time to Expiration (days):", min_value = 0, value = 30) # days
    premium = st.sidebar.number_input("Option Premium:", min_value = 0.0, value = 5.0)
    interest_rate = st.sidebar.number_input("Risk Free Interest Rate:", min_value = 0.01, value=0.03)
    
    position = st.sidebar.selectbox("Type of Position", options = ['Buy (Long)', 'Sell (Short)'])
    option_type = st.sidebar.selectbox("Type of Option", options = ['Call (📈)', 'Put (📉)'])

    # Evaluate to correct input
    position = evaluate_position(position)
    option_type = evaluate_option_type(option_type)
    
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        black_scholes_merton_initialise_request(interest_rate, spot_price, strike_price, time, sigma, \
                                   premium, position, option_type)
        greeks = black_scholes_merton_get_greeks()
        plot_payoffs = black_scholes_merton_plot_payoff()
        value = compare_prices(greeks["payload"]["option_price"], premium)
        
        st.markdown("**Greek Values**")
        st.dataframe(greeks["payload"], use_container_width = True)

        st.markdown(f"**{position.capitalize()} Payoff Diagram of a {option_type.capitalize()} Option**")
        st.image(plot_payoffs)

        st.markdown("**Comparing Black-Scholes-Merton-Calculated Premium against User Input Premium**")
        st.dataframe({"Theoretical Option Price": greeks["payload"]["option_price"], "Actual Option Price": premium}, use_container_width = True)
        st.caption(f"The actual option price is {value}.")

# Layout for the application
def main():
    st.header("Black Scholes Merton for Stock Options")
    st.markdown("This function uses the Black Scholes Merton model to generate key insights for a chosen stock option.")
    st.caption("Select your variables in the column on the left.")
    "---"

    st.write("##### Output")
    sidebar()
    
if __name__ == "__page__":
    main()
