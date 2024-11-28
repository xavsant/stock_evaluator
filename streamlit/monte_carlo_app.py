# Imports
import streamlit as st
from requests import post as rpost

# Plot Imports
import plotly.graph_objects as go
from json import loads
from PIL import Image
from io import BytesIO

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

    stock_symbols = st.sidebar.multiselect("Select Portfolio of Stock:", options = ['AAPL', 'TSLA', 'NVDA'], default = ['AAPL', 'NVDA'])
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
        st.write(key_data)
        st.plotly_chart(plot_simulation_lines, use_container_width=True)
        st.plotly_chart(plot_simulation_avg, use_container_width=True)
        st.plotly_chart(plot_individual_cumulative_returns, use_container_width=True)
        st.plotly_chart(plot_histogram_with_risk_metrics, use_container_width=True)
        st.image(plot_corr_heatmap)
        st.image(risk_metrics)

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



# from requests import post as rpost

# def sentiment_request(stock: str):
#      header = {"Content-Type": "application/json"}

#      parameters = {"stock": stock}

#      response = rpost(
#           url="http://0.0.0.0:8000/stock_sentiment_analysis",
#           headers=header,
#           params=parameters
#      )

#      return response.json()

# def article_colour(summary: str):
#     if summary.lower() == "optimistic":
#         colour = ':green'
#     elif summary.lower() == "pessimistic":
#         colour = ':red'
#     else:
#         colour = ':orange'

#     return colour

# def overall_sentiment(sentiment_summary_payload: dict):
#     summary = max(sentiment_summary_payload, key=sentiment_summary_payload.get)
#     colour = article_colour(summary)

#     return summary, colour

# def display_articles(sentiment_article_payload: dict):
#     count = 1
#     for article in sentiment_article_payload:
#         title = str(count) + ' &mdash; ' + article_colour(article["sentiment"]) + '[' + article["headline"] + ']'

#         st.markdown(f'{title}  \n  {article["hyperlink"]}')

#         count += 1
    
# def display_response(sentiment_payload: dict):
#     sentiment, colour = overall_sentiment(sentiment_payload["summary"])

#     st.markdown(f'### {sentiment_payload["stock name"]}')
#     st.markdown(f'The overall sentiment of {sentiment_payload["stock name"]} is **{colour}[' + sentiment + ']**.')

#     display_articles(sentiment_payload["articles"])

#     st.markdown("---")
#     st.markdown("##### Legend")
#     st.markdown(
#         """
#         - **Optimistic**: 🟢 :green[Green]  
#         - **Neutral**: 🟠 :orange[Orange]  
#         - **Pessimistic**: 🔴 :red[Red]
#         """
#     )


# # ---
# # Layout
# # ---
# def sidebar():
#     st.sidebar.title("Input Variables")

#     stock = st.sidebar.selectbox("Select Stock:", options = ['AAPL', 'TSLA', 'NVDA'],)
    
#     generate_button = st.sidebar.button("Generate")

#     if generate_button:
#         sentiment_response = sentiment_request(stock) # add error handling
#         # st.write(sentiment_response)
#         display_response(sentiment_response["payload"])

# def main():
#     st.header("Sentiment Analysis")
#     st.markdown("For a chosen stock, this function searches Yahoo Finance for the latest news and  \n  \
#                 gets the latest sentiment (individual + overall) using a trained model.  \n  \
#                 Select your variables in the column on the left.")
#     "---"

#     st.write("#### Output")
#     sidebar()
    
# if __name__ == "__page__":
#     main()