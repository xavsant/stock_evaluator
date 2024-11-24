# Imports
import streamlit as st

# Mock backend function
def backend_function(variable):
    return f"Data sent to backend: {variable}"

def sidebar():
    st.sidebar.title("Input Variables")

    portfolio = st.sidebar.selectbox("Select Portfolio of Stock:", options = ['AAPL', 'TSLA', 'NVDA']) # get Current Stock Price
    risk_free_interest_rate = st.sidebar.number_input("Risk Free Interest Rate:", min_value = 0.04) 
    market_price = st.sidebar.number_input("Market Price:", min_value = 0) # from stock, filled up automatically
    strike_price = st.sidebar.number_input("Strike Price:", min_value = 0)
    time_to_expiration = st.sidebar.number_input("Time to Expiration (days):", min_value = 0) # days
    volatility = st.sidebar.number_input("Volatility:", min_value = 0.00) # from stock, filled up automatically
    type_option = st.sidebar.selectbox("Type of Option", options = ['Call (📈)', 'Put (📉)'])
    type_position = st.sidebar.selectbox("Type of Position", options = ['Buy (Long)', 'Sell (Short)'])
    option_premium = st.sidebar.number_input("Option Premium:", min_value = 0)
    
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        result = backend_function([portfolio, risk_free_interest_rate, market_price, strike_price, time_to_expiration, volatility,\
                                   type_option, type_position, option_premium])
        st.write(result)

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
