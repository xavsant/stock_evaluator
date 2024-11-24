# Imports
import streamlit as st

# Mock backend function
def backend_function(variable):
    return f"Data sent to backend: {variable}"

def popover_weights(portfolio):
    num_stocks = len(portfolio)
    default_weight = 1 / num_stocks

    with st.sidebar.popover("Adjust weights"):
        weights = {}
        for stock in portfolio:
            weights[stock] = st.number_input(
                f"Weight for {stock}",
                min_value=0.0,
                max_value=1.0,
                value=default_weight,
                step=0.01,
                key=f"weight_{stock}",
            )

        # Check if weights sum to 1
        if round(sum(weights.values()), 2) != 1:
            st.error("Sum of weights is not equal to 1")

    return weights

def sidebar():
    st.sidebar.title("Input Variables")

    portfolio = st.sidebar.multiselect("Select Portfolio of Stock:", options = ['AAPL', 'TSLA', 'NVDA'], default = ['AAPL', 'NVDA'])
    portfolio_value = st.sidebar.number_input("Value of Portfolio:", value = 10000) # to change
    portfolio_weights = popover_weights(portfolio) # to change
    historical_timeframe = st.sidebar.slider("Historical Range (days):", value = 365, min_value = 90, max_value = 1825)
    forecast_timeframe = st.sidebar.slider("Forecast Range (days):", value = 30, min_value = 30, max_value = 365)
    number_of_simulations = st.sidebar.slider("Number of Simulations:", value = 100, min_value = 100, max_value = 1000)
    
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        result = backend_function([portfolio, portfolio_value, portfolio_weights, historical_timeframe, forecast_timeframe, number_of_simulations])
        st.write(result)

# Layout for the application
def main():
    st.header("Monte Carlo Simulation")
    st.markdown("This function generates results for a Monte Carlo Simulation of a chosen portfolio of stock.  \n  \
                Select your variables in the column on the left.")
    "---"

    st.write("### Output")
    sidebar()
    
if __name__ == "__page__":
    main()