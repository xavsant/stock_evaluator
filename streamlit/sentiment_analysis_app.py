# Imports
import streamlit as st
from requests import post as rpost
from os import environ

# Initialise POST URL
backend_url = environ["BACKEND_URL"]

def get_tickers():
    if "tickers" in st.session_state:
        return st.session_state.tickers
    else:
        st.warning("No tickers initialized. Please restart the app.")

def sentiment_request(stock: str):
    header = {"Content-Type": "application/json"}

    parameters = {"stock": stock}
     
    response = rpost(
    url=backend_url+"/stock_sentiment_analysis",
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
        with st.container(border=True):
            # title = str(count) + ' &mdash; ' + article_colour(article["sentiment"]) + '[' + article["headline"] + ']'
            title = str(count) + ' &mdash; ' + article["headline"]
            sentiment = 'Sentiment: ' + article_colour(article["sentiment"]) + '[' + article["sentiment"] + ']'

            st.markdown(f'###### {title}  \n  {sentiment}  \n  {article["hyperlink"]}')

        count += 1
    
def display_response(sentiment_payload: dict):
    sentiment, colour = overall_sentiment(sentiment_payload["summary"])

    st.markdown(f'### {sentiment_payload["stock name"]}')
    st.markdown(f'The overall sentiment of {sentiment_payload["stock name"]} is **{colour}[' + sentiment + ']**.')

    display_articles(sentiment_payload["articles"])

# ---
# Layout
# ---
def sidebar():
    st.sidebar.title("Input Variables")

    # Initialize session state variables if they don't exist
    if 'generated' not in st.session_state:
        st.session_state.generated = False
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = get_tickers()[9]  # Default to index 9
    if 'sentiment_results' not in st.session_state:
        st.session_state.sentiment_results = None

    stock = st.sidebar.selectbox("Select Stock:", 
                               options=get_tickers(), 
                               index=get_tickers().index(st.session_state.selected_stock))
    
    generate_button = st.sidebar.button("Generate")

    if generate_button:
        sentiment_response = sentiment_request(stock)

        if sentiment_response["success"]:
            st.session_state.sentiment_results = sentiment_response
            st.session_state.generated = True
            st.session_state.selected_stock = stock

        else:
            st.error(f"The web scraper encountered difficulties accessing {stock},  \n  please visit https://finance.yahoo.com/quote/{stock}/ directly instead.")

    # Display saved results if they exist
    if st.session_state.generated and st.session_state.sentiment_results:
        display_response(st.session_state.sentiment_results["payload"])

def main():
    st.header("Sentiment Analysis")
    st.markdown("For a chosen stock, this function searches Yahoo Finance for the latest news and  \n  \
                gets the latest sentiment (individual + overall) using a trained model.")
    st.caption("Select your variables in the column on the left.")
    with st.expander("More information"):
        st.markdown("""
                    The sentiment analysis function can be split into 3 sub-processes.
                    ###### 1) Web Scraping
                    For a particular stock, the function :blue[scrapes Yahoo Finance for news on that stock] using Python's BeautifulSoup4 package. It first scrapes the webpage for all news article URLs relating to that stock and stores them into a list. Subsequently, the function scrapes each URL of its headline and body of text and stores them into another list.
                    ###### 2) Training the sentiment analysis model
                    The sentiment analysis model was trained using the :blue[Maximum Entropy classification model from Python's NLTK and Gensim packages]. In order to train the model, we curated 100 news articles from Yahoo Finance and manually categorized them into their overall sentiment towards a particular stock, consisting of 34 optimistic, 33 neutral, and 33 pessimistic articles. We then trained the classifier model based on these 100 curated labelled articles to recognize and classify new unseen news articles into these 3 categories. After training, the model was then saved using Python's pickle package.
                    ###### 3) Combining the scraped articles and sentiment analysis model into a sentiment analysis application
                    The scraped articles and trained sentiment analysis model are combined and developed into a sentiment analysis application. The application takes in a :red[ticker symbol] as its input and outputs the sentiment of each scraped article. It does this by applying the trained classifier model on each news article stored in the corpus of scraped articles. :blue[The headline and hyperlink of each article is also shown in the output to enable the user to click and read each article if they are interested.] Furthermore, the function summarises and outputs the overall sentiment towards the stock based on the count of each predicted sentiment.
                    
                    From this application, users will be able to predict the expected overall sentiment of a particular stock in a relatively short amount of time based on the textual sentiment of financial experts. Users can then base their investment decision based on sound financial advice without spending hours skimming through financial news. Note, however, that this is meant to assist and not replace the human element of investing.
                    """)
    "---"

    sidebar()
    
if __name__ == "__page__":
    main()
