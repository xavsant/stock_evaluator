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

    # Initialize session state variables if they don't exist
    if 'generated' not in st.session_state:
        st.session_state.generated = False
    if 'bsm_results' not in st.session_state:
        st.session_state.bsm_results = None
    if 'time' not in st.session_state:
        st.session_state.time = 30
    if 'premium' not in st.session_state:
        st.session_state.premium = 5.0
    if 'interest_rate' not in st.session_state:
        st.session_state.interest_rate = 0.03
    if 'position' not in st.session_state:
        st.session_state.position = 'Buy (Long)'
    if 'option_type' not in st.session_state:
        st.session_state.option_type = 'Call (📈)'

    # Get real-time data from API
    stock_data = stock_spot_and_volatility()
    spot_price = stock_data["spot_price"]
    sigma = stock_data["volatility"]
    strike_price = stock_data["spot_price"] - 5  # Default strike price to spot price -5
    
    # Display the API-fetched values
    st.sidebar.number_input("Spot Price:", min_value=0.0, value=spot_price, disabled=True)
    sigma = st.sidebar.number_input("Volatility:", min_value=0.0, value=sigma)
    strike_price = st.sidebar.number_input("Strike Price:", min_value=0.0, value=strike_price)
    
    # Use session state for other inputs
    time = st.sidebar.number_input("Time to Expiration (days):", min_value=0, key='time')
    premium = st.sidebar.number_input("Option Premium:", min_value=0.0, key='premium')
    interest_rate = st.sidebar.number_input("Risk Free Interest Rate:", min_value=0.01, key='interest_rate')
    position = st.sidebar.selectbox("Type of Position", options=['Buy (Long)', 'Sell (Short)'], key='position')
    option_type = st.sidebar.selectbox("Type of Option", options=['Call (📈)', 'Put (📉)'], key='option_type')

    # Evaluate to correct input
    position = evaluate_position(position)
    option_type = evaluate_option_type(option_type)
    
    # Single generate button
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        black_scholes_merton_initialise_request(interest_rate, spot_price, strike_price, time, sigma,
                                              premium, position, option_type)
        
        # Store all results in session state
        st.session_state.bsm_results = {
            'greeks': black_scholes_merton_get_greeks(),
            'plot_payoffs': black_scholes_merton_plot_payoff(),
            'position': position,
            'option_type': option_type,
            'premium': premium
        }
        st.session_state.generated = True

    # Display saved results if they exist
    if st.session_state.generated and st.session_state.bsm_results:
        results = st.session_state.bsm_results
        
        st.markdown(f"**{results['position'].capitalize()} Payoff Diagram of a {results['option_type'].capitalize()} Option**")
        st.image(results['plot_payoffs'])

        with st.container(border=True):
            st.markdown("**Greek Values**")
            st.dataframe(results['greeks']["payload"], use_container_width=True)
            with st.popover("Information on Greeks"):
                st.markdown("""
                            ###### **option_price** 
                            The option price (also known as the premium) is the market price of an option. It represents the cost to purchase the option contract and is influenced by various factors such as the underlying asset price, strike price, time to expiration, implied volatility, and interest rates. It is typically calculated using the Black-Scholes-Merton (BSM) model, which is a widely used mathematical model for pricing European-style options.
                            
                            **delta**
                            Delta is a measure of the change in an option's price or premium resulting from a change in the underlying asset. It provides an estimate of how much the option price will move for a small change in the underlying asset's price. A delta of 0.5 means the option's price will increase by \$0.50 for every \$1 increase in the underlying asset.
                            
                            **gamma**
                            Gamma measures the rate of change of delta as the price of the underlying asset changes. It helps forecast how much the delta will change for a given change in the underlying asset's price. It also provides insights into the curvature of the option's price curve relative to the underlying asset, indicating the potential for larger price movements as the underlying asset fluctuates.
                            
                            **vega**
                            Vega measures the risk of changes in implied volatility or the forward-looking expected volatility of the underlying asset price. As implied volatility increases, the price of options tends to rise, and vega quantifies how much the price of an option will change with a 1% change in implied volatility. This is especially important for options traders who anticipate volatility changes in the market.
                            
                            **theta**
                            Theta measures time decay in the value of an option or its premium. It shows how much the value of an option decreases as time passes, all else being equal. A higher absolute theta indicates faster time decay, which is crucial for option holders and sellers to understand, especially as expiration dates approach.
                            
                            **rho**
                            Rho measures an option's sensitivity to changes in the risk-free rate of interest. It indicates how much the price of an option will increase or decrease in response to a 1% change in the risk-free interest rate. Rho is particularly relevant when considering economic conditions and central bank policy, as changes in interest rates can impact options pricing.
                            """)

            st.markdown("**Comparing Black-Scholes-Merton-Calculated Premium against User Input Premium**")
            value = compare_prices(results['greeks']["payload"]["option_price"], results['premium'])
            st.dataframe({
                "Theoretical Option Price": results['greeks']["payload"]["option_price"], 
                "Actual Option Price": results['premium']
            }, use_container_width=True)
            st.text(f"The premium you've entered is {value}.")

# Layout for the application
def main():
    st.header("Black Scholes Merton for Stock Options")
    st.markdown("This function uses the Black Scholes Merton model to generate key insights for a chosen stock option.")
    st.caption("Select your variables in the column on the left.")
    with st.popover("More information"):
        st.markdown("""
                    The Black-Scholes-Merton model is a mathematical formula used to calculate the theoretical price of options. It assumes that the price of the underlying asset follows a :blue[geometric Brownian motion and that there are no arbitrage opportunities].
                    
                    The model takes into account key factors such as the :red[stock price, strike price, risk-free interest rate, time to expiration, and volatility] to determine an option's price. 
                    
                    The application also asks for the :red[actual option premium, type of position and type of option] to determine the payoffs and whether the actual option price is under or overpriced as determined by the model.
                    """)
    "---"

    sidebar()
    
if __name__ == "__page__":
    main()
