# Web Scraper
from backend.utils.data_fetching import WebScraper

# Sentiment Analysis
import nltk
from nltk.util import ngrams
# nltk.download('stopwords')
import contractions
import pickle

# Utility
import os

# Get directory of pickled models
base_dir = os.path.dirname(os.path.abspath(__file__))
dictionary_path = os.path.join(base_dir, "models", "dictionary.pkl")
maxent_sentiment_classifier_path = os.path.join(base_dir, "models", "maxent_sentiment_classifier.pkl")

class SentimentAnalysis:
    def __init__(self):
        with open(dictionary_path, "rb") as f:
            self.dictionary = pickle.load(f)
        with open(maxent_sentiment_classifier_path, "rb") as f:
            self.classifier = pickle.load(f)
        self.stop_list = nltk.corpus.stopwords.words('english')
        self.lemmatizer = nltk.stem.WordNetLemmatizer()

    def preprocess_text(self, text):
        article = nltk.word_tokenize(text)
        article = [w.lower() for w in article if w.isalnum() and w not in self.stop_list]
        article = [self.lemmatizer.lemmatize(contractions.fix(w)) for w in article]
        bigrams = [' '.join(w) for w in list(ngrams(article, 2))]
        article.extend(bigrams)
        return article

    def predict_sentiment(self, text):
        article = self.preprocess_text(text)
        vector = self.dictionary.doc2bow(article)
        article_as_dict = {id: 1 for (id, tf) in vector}
        return self.classifier.classify(article_as_dict)
    
class Stock_SentimentAnalysis:
    def __init__(self, stock):
        self.stock = stock
        
        try:
            self.scraper = WebScraper(stock)
        except ValueError as e:
            raise e
        
        self.analyzer = SentimentAnalysis()
        self.articles = []
        self.sentiment_count = {'optimistic': 0, 'neutral': 0, 'pessimistic': 0}

    def run(self):
        self.scraper.search_stock()
        self.scraper.scrape_articles()

        for (headline, article, hyperlink) in zip(self.scraper.headline_list, self.scraper.article_list, self.scraper.hyperlink_list):
            sentiment = self.analyzer.predict_sentiment(article)
            self.articles.append({'headline': headline, 'sentiment': sentiment, 'hyperlink': hyperlink})
            self.sentiment_count[sentiment.lower()] += 1

        #print("Summary:")
        #for (sentiment, count) in self.sentiment_count.items():
        #    print(f"{sentiment.capitalize()}: {count}\t", end="")

        #overall_sentiment = max(self.sentiment_count, key=self.sentiment_count.get)
        #print(f"\nThe overall sentiment for {self.scraper.stock_name} is {overall_sentiment.capitalize()}.")

        return self._package_output(self.scraper.stock_name, self.articles, self.sentiment_count)

    def _package_output(self, stock_name: str, articles: dict, summary: dict):
        return {'stock name': stock_name, 'articles': articles, 'summary': summary}

if __name__ == "__main__":
    stock = input("Enter a Stock: ")
    app = Stock_SentimentAnalysis(stock)
    result = app.run()
    print(result)
