# Imports
import streamlit as st
from requests import post as rpost
from os import environ

# Plot Imports
import plotly.graph_objects as go
from json import loads
from PIL import Image
from io import BytesIO

# Utility
from requests.exceptions import ConnectionError
from PIL.Image import Image as PIL_Image
from plotly.graph_objects import Figure

# Initialise POST URL
backend_url = environ["BACKEND_URL"]

# Initialize tabs
tab_simulation, tab_correlation_matrix, tab_simulation_average, tab_individual_cumulative_returns, tab_var_histogram, tab_risk_metrics_summary_table = st.tabs(["Simulation", "Correlation Matrix", "Simulation Average", "Individual Cumulative Returns", "VaR Histogram", "Risk Metrics Summary Table"])

def get_tickers() -> str:
    if "tickers" in st.session_state:
        return st.session_state.tickers
    else:
        st.warning("No tickers initialised. Please restart the app.")
        return []

def monte_carlo_initialise_request(stock_symbols: list, num_each_stock: list, historical_timeframe: int, forecast_timeframe: int, num_simulations: int) -> dict:
     header = {"Content-Type": "application/json"}

     parameters = {
         "stock_symbols": stock_symbols,
         "num_each_stock": num_each_stock,
         "historical_timeframe": historical_timeframe,
         "forecast_timeframe": forecast_timeframe,
         "num_simulations": num_simulations
         }

     response = rpost(
          url=backend_url+"/initialise_monte_carlo",
          headers=header,
          json=parameters
     )

     return response.json()

def monte_carlo_get_key_data() -> dict:
    header = {"Content-Type": "application/json"}

    response = rpost(
          url=backend_url+"/monte_carlo/key_data",
          headers=header
     )

    return response.json()

def monte_carlo_plot_simulation_lines() -> Figure:
    response = rpost(
          url=backend_url+"/monte_carlo/plot_simulation_lines"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_simulation_avg() -> Figure:
    response = rpost(
          url=backend_url+"/monte_carlo/plot_simulation_avg"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_individual_cumulative_returns() -> Figure:
    response = rpost(
          url=backend_url+"/monte_carlo/plot_individual_cumulative_returns"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_histogram_with_risk_metrics() -> Figure:
    response = rpost(
          url=backend_url+"/monte_carlo/plot_histogram_with_risk_metrics"
     )

    plot_json = response.json()
    fig = go.Figure(loads(plot_json))

    return fig

def monte_carlo_plot_corr_heatmap() -> PIL_Image:
    header = {"Content-Type": "application/json"}

    response = rpost(
          url=backend_url+"/monte_carlo/plot_corr_heatmap",
          headers=header,
          stream=True
    )

    response_image = Image.open(BytesIO(response.content))

    return response_image

def monte_carlo_generate_risk_metrics() -> PIL_Image:
    header = {"Content-Type": "application/json"}

    response = rpost(
          url=backend_url+"/monte_carlo/generate_risk_metrics",
          headers=header,
          stream=True
    )

    response_image = Image.open(BytesIO(response.content))

    return response_image

def show_explanatory_text():
    st.header("Monte Carlo Simulations")
    st.markdown("This function generates results for Monte Carlo simulations of a chosen portfolio of stock.")
    st.caption("Select your variables in the column on the left.")
    with st.popover("More information"):
        st.markdown("""
                    This Monte Carlo simulation works by generating random samples from a :blue[multivariate normal distribution] for each stock, which accounts for the correlations between the stocks in the portfolio.
                    The random samples represent the potential daily returns for each stock, and the covariance matrix is used to model the correlation structure between the stocks. The simulation generates random price paths based on these returns, reflecting various possible future market scenarios. 
                    
                    To run the simulation, the model takes into account key factors such as the :red[stocks in the portfolio, shares per stock, historical range to predict the future, forecast range, and number of simulations to run].
                    """)
    "---"

def show_simulation(key_data, plot_simulation_lines, plot_corr_heatmap, plot_simulation_avg, \
                    plot_individual_cumulative_returns, plot_histogram_with_risk_metrics, risk_metrics):
    # Only show explanatory text in tabs after generation
    with tab_simulation:
        show_explanatory_text()
        st.markdown("**Portfolio Summary**")
        st.dataframe(key_data, use_container_width = True)
        st.caption(f"The initial value of your portfolio is {round(st.session_state.portfolio_value, 4)}.")
        st.plotly_chart(plot_simulation_lines, use_container_width=True)

    with tab_correlation_matrix:
        show_explanatory_text()
        st.markdown("**Stock Correlation Matrix**")
        st.image(plot_corr_heatmap)
        with st.expander("More information"):
            st.markdown("""
                        The **correlation matrix** displays the correlation coefficients between multiple assets in a stock portfolio. Each cell in the matrix quantifies the relationship between two assets, with values ranging from **-1** to **+1**:
                        
                        - **+1**: Perfect positive correlation (assets move in the same direction).
                        - **0**: No correlation (assets move independently).
                        - **-1**: Perfect negative correlation (assets move in opposite directions).
                        
                        ###### Importance of Diversification
                        Understanding correlations is critical for diversification. A well-diversified portfolio includes assets with low or negative correlations, which helps:
                         
                        - **Reduce Risk**: Decreases the likelihood of all assets declining simultaneously during market downturns.
                        - **Stabilise Returns**: Mitigates portfolio volatility and smooths performance over time.
                        - **Enhance Resilience**: Balances gains and losses, ensuring more consistent long-term growth.
                        
                        Use the correlation matrix to identify relationships between assets and build a robust portfolio.
                        """)

    with tab_simulation_average:
        show_explanatory_text()
        st.plotly_chart(plot_simulation_avg, use_container_width=True)
        with st.popover("More information"):
            st.markdown("This function visualises the average cumulative return of simulated portfolio values over time, helping users to track the portfolio's expected performance trajectory. ")

    with tab_individual_cumulative_returns:
        show_explanatory_text()
        st.plotly_chart(plot_individual_cumulative_returns, use_container_width=True)

    with tab_var_histogram:
        show_explanatory_text()
        st.plotly_chart(plot_histogram_with_risk_metrics, use_container_width=True)

        # Legend
        st.markdown("""
                    **Legend**: 
                    - **:red[VaR (5%)]**:
                    Represented by the **:red[red dotted line]**, the Value at Risk indicates the threshold below which 5% of portfolio values are expected to fall.
                    - **:orange[CVaR (5%)]**:
                    Represented by the **:orange[orange dotted line]**, the Conditional Value at Risk represents the average of all portfolio values below the VaR threshold.
                    """)

    with tab_risk_metrics_summary_table:
        show_explanatory_text()
        st.markdown("**Risk Metrics Summary Table**")
        st.image(risk_metrics)
        with st.popover("More information"):
            st.markdown("""
                        This table summarises the portfolio performance and offers insights based on their levels, guiding users on potential adjustments and optimisation strategies.
                        - **Sharpe Ratio**:
                        A risk-adjusted performance measure that compares the excess return of the portfolio (over the risk-free interest rate) to its standard deviation. A higher Sharpe ratio indicates that the portfolio is providing more return per unit of risk, making it more efficient. A ratio above 1 is considered good, signaling that the portfolio is generating a favorable return relative to the risk taken. A ratio below 1 may suggest that the portfolio’s returns are not sufficient to justify the risk involved.

                        """)

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

# ---
# Layout
# ---
def sidebar():
    st.sidebar.title("Input Variables")

    # Initialize session state variables
    if 'generated' not in st.session_state:
        st.session_state.generated = False
    if 'monte_carlo_results' not in st.session_state:
        st.session_state.monte_carlo_results = None
    if 'portfolio_value' not in st.session_state:
        st.session_state.portfolio_value = None
    if 'stock_symbols' not in st.session_state:
        st.session_state.stock_symbols = ['AAPL', 'AMZN', 'MSFT', 'NVDA', 'TSLA']
    if 'historical_timeframe' not in st.session_state:
        st.session_state.historical_timeframe = 365
    if 'forecast_timeframe' not in st.session_state:
        st.session_state.forecast_timeframe = 30
    if 'num_simulations' not in st.session_state:
        st.session_state.num_simulations = 100
    
    stock_symbols = st.sidebar.multiselect("Select Portfolio of Stock:", 
                                         options=get_tickers(), 
                                         default=st.session_state.stock_symbols)
    num_each_stock = popover_shares(stock_symbols)
    historical_timeframe = st.sidebar.slider("Historical Range (days):", 
                                           value=st.session_state.historical_timeframe,
                                           min_value=90, 
                                           max_value=1825,
                                           step=10)
    forecast_timeframe = st.sidebar.slider("Forecast Range (days):", 
                                         value=st.session_state.forecast_timeframe,
                                         min_value=30, 
                                         max_value=365,
                                         step=5)
    num_simulations = st.sidebar.slider("Number of Simulations:", 
                                      value=st.session_state.num_simulations,
                                      min_value=100, 
                                      max_value=1000,
                                      step=50)

    generate_button = st.sidebar.button("Generate")

    if generate_button:
        # Save current parameters
        st.session_state.stock_symbols = stock_symbols
        st.session_state.historical_timeframe = historical_timeframe
        st.session_state.forecast_timeframe = forecast_timeframe
        st.session_state.num_simulations = num_simulations
        st.session_state.num_each_stock = num_each_stock

        try:
            st.session_state.generated = True
            
            monte_carlo_initialise_request(st.session_state.stock_symbols, list(st.session_state.num_each_stock.values()), 
                                        st.session_state.historical_timeframe, st.session_state.forecast_timeframe, st.session_state.num_simulations)
            
            # Get key data and store portfolio value separately
            key_data = monte_carlo_get_key_data()
            st.session_state.portfolio_value = key_data.pop("portfolio_value")
            
            # Store all results in session state
            st.session_state.monte_carlo_results = {
                'key_data': key_data,
                'plot_simulation_lines': monte_carlo_plot_simulation_lines(),
                'plot_simulation_avg': monte_carlo_plot_simulation_avg(),
                'plot_individual_cumulative_returns': monte_carlo_plot_individual_cumulative_returns(),
                'plot_histogram_with_risk_metrics': monte_carlo_plot_histogram_with_risk_metrics(),
                'plot_corr_heatmap': monte_carlo_plot_corr_heatmap(),
                'risk_metrics': monte_carlo_generate_risk_metrics()
            }
        except ConnectionError:
            st.info("The backend is currently unreachable. It might be waking up. Please try again in a few moments.")
        except Exception as e:
            st.error(f"Encountered an unhandled exception: {type(e).__name__}. Please report this issue to the repository owner for assistance.")

def main():
    sidebar()
    
    # Show either the initial explanatory text or the results
    if not st.session_state.generated:
        show_explanatory_text()
    elif st.session_state.monte_carlo_results:
        results = st.session_state.monte_carlo_results
        show_simulation(results['key_data'], 
                       results['plot_simulation_lines'],
                       results['plot_corr_heatmap'], 
                       results['plot_simulation_avg'],
                       results['plot_individual_cumulative_returns'], 
                       results['plot_histogram_with_risk_metrics'], 
                       results['risk_metrics'])

# Layout for the application
if __name__ == "__page__":
    main()