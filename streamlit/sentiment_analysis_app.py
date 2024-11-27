# Imports
import streamlit as st
from requests import post as rpost

def sentiment_request(stock: str):
     header = {"Content-Type": "application/json"}

     parameters = {"stock": stock}

     response = rpost(
          url="http://0.0.0.0:8000/stock_sentiment_analysis",
          headers=header,
          params=parameters
     )

     return response.json()

def article_colour(summary: str):
    if summary.lower() == "optimistic":
        colour = ':green'
    elif summary.lower() == "pessimistic":
        colour = ':red'
    else:
        colour = ':orange'

    return colour

def overall_sentiment(sentiment_summary_payload: dict):
    summary = max(sentiment_summary_payload, key=sentiment_summary_payload.get)
    colour = article_colour(summary)

    return summary, colour

def display_articles(sentiment_article_payload: dict):
    count = 1
    for article in sentiment_article_payload:
        title = str(count) + ' &mdash; ' + article_colour(article["sentiment"]) + '[' + article["headline"] + ']'

        st.markdown(f'{title}  \n  {article["hyperlink"]}')

        count += 1
    
def display_response(sentiment_payload: dict):
    sentiment, colour = overall_sentiment(sentiment_payload["summary"])

    st.markdown(f'### {sentiment_payload["stock name"]}')
    st.markdown(f'The overall sentiment of {sentiment_payload["stock name"]} is **{colour}[' + sentiment + ']**.')

    display_articles(sentiment_payload["articles"])

    st.markdown("---")
    st.markdown("##### Legend")
    st.markdown(
        """
        - **Optimistic**: 🟢 :green[Green]  
        - **Neutral**: 🟠 :orange[Orange]  
        - **Pessimistic**: 🔴 :red[Red]
        """
    )


# ---
# Layout
# ---
def sidebar():
    st.sidebar.title("Input Variables")

    stock = st.sidebar.selectbox("Select Stock:", options = ['AAPL', 'TSLA', 'NVDA'],)
    
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        sentiment_response = sentiment_request(stock) # add error handling
        # st.write(sentiment_response)
        display_response(sentiment_response["payload"])

def main():
    st.header("Sentiment Analysis")
    st.markdown("For a chosen stock, this function searches Yahoo Finance for the latest news and  \n  \
                gets the latest sentiment (individual + overall) using a trained model.  \n  \
                Select your variables in the column on the left.")
    "---"

    st.write("#### Output")
    sidebar()
    
if __name__ == "__page__":
    main()
