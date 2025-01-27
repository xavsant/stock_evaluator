# Stock Evaluator

## Index:
1. [Description](#1-description)  
2. [Structure](#2-structure)  
3. [Dependencies](#3-dependencies)  
4. [Running the Project](#4-running-the-project)  
5. [To-Do](#5-to-do)  
6. [Bugs](#6-bugs)  
7. [Authors](#7-authors) 

---
 
### [1] Description

Web Application for Portfolio Stock Evaluation using Monte Carlo simulations, Black-Scholes-Merton model for Stock Options, and Sentiment Analysis. Provides a comprehensive overview of a chosen stock/portfolio based on Gaussian simulations, theoretical option premium calculations, and article reviews.

The backend of this project is hosted on Render, and the frontend on Streamlit. Finnhub's API is used to access NASDAQ tickers.

#### **Functions**
- Monte Carlo Simulations
![Web Application](./notebooks/screenshots/Monte_Carlo_Simulations_screenshot.png)

- Black-Scholes-Merton
![Web Application](./notebooks/screenshots/Black_Scholes_Merton_screenshot.png)

- Sentiment Analysis
![Web Application](./notebooks/screenshots/Sentiment_Analysis_screenshot.png)


---

### [2] Structure
```
stock_evaluator/
│
├── app.py                              # Streamlit app
│
├── streamlit/                          # Streamlit pages
│   ├── black_scholes_merton_app.py
│   ├── monte_carlo_app.py
│   └── sentiment_analysis_app.py 
│
├── backend/
│   ├── __init__.pys
│   ├── black_scholes_merton.py
│   ├── monte_carlo.py
│   ├── sentiment_analysis.py  
│   ├── main.py                         # FastAPI app  
│   ├── utils/                          # Helper functions
│   │   ├── __init__.py
│   │   └── data_fetching.py            # Functions to fetch stock data
│   └── models/     
│       ├── __init__.py            
│       └── maxent_sentiment_classifier.pkl
│       └── ...         
│
├── notebooks/
│   └── ...                             # For feature experimentation
│
├── Dockerfile                          # Backend Docker container
├── requirements.txt                    # Dependencies
└── README.md
```

---

### [3] Dependencies

#### **Python**
- python = "^3.11"

#### **General Packages**
- [numpy](https://pypi.org/project/numpy/)
- [pandas](https://pypi.org/project/pandas/)
- [yfinance](https://pypi.org/project/yfinance/)

#### **Interface**
- [fastapi](https://pypi.org/project/fastapi/)
- [streamlit](https://pypi.org/project/streamlit/)

#### **Function-Exclusive Packages**

*Black Scholes Merton*
- [scipy](https://pypi.org/project/scipy/)

*Sentiment Analysis*
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [contractions](https://pypi.org/project/contractions/)
- [gensim](https://pypi.org/project/gensim/)
- [nltk](https://pypi.org/project/nltk)

#### **Plotting**
- [matplotlib](https://pypi.org/project/matplotlib/)
- [plotly](https://pypi.org/project/plotly/)
- [seaborn](https://pypi.org/project/seaborn/)

> Refer to requirements.txt for more information on dependencies

---

### [4] Running the project

#### **Exporting Dependencies**
If any packages/dependencies are updated via poetry, be sure to export the requirements.txt using the following:
`poetry export --without-hashes -f requirements.txt -o requirements.txt`

#### **Import Behaviour in Different Environments:**

*End-State*
  When the app is running as a complete system (e.g., containerised in Docker, or through app.py or main.py), imports use **absolute file paths**. For example:
  `from backend.utils.data_fetching import WebScraper`

*Running Individual Files*
  When running specific files like app.py or main.py independently, import paths need to be adjusted. For example:
  `from utils import WebScraper`

This difference is due to how file execution context affects module resolution between a full system setup and individual file execution.

#### **Live version:**
- [Frontend](https://stock-evaluator-30590.streamlit.app)
- [Interactive Backend](https://stock-evaluator-djr5.onrender.com/docs)

> The backend may take time to re-deploy if asleep

#### **Running Locally with Docker (Backend only):**
1. Run `docker build -t image_name -f Dockerfile_backend .` in your command line
2. Run `docker run -p 0.0.0.0:80:80 image_name`
3. Open up `0.0.0.0:80/docs`

#### **Locally without Docker**
1. Frontend: Run `streamlit run app.py` in your command line
2. Backend: Run `fastapi run backend/main.py` in your command line
  - Access API Docs: [For interactively testing backend functions](http://0.0.0.0:8000/docs)

---

### [5] To-Do
- TD1: Clean up streamlit pages by moving functions to another .py
- TD2: Edit WebScraper class to behave in a more OOP way, returning objects
- TD3: Only use pickle for models, use JSON for dict
- TD4: Edit risk metrics summary table to return data to frontend, instead of image (create table in streamlit)
- TD5: Edit black scholes plot payoff and risk metrics summary table to fit with design of streamlit UI
- TD6: Input descriptive information for streamlit pages from JSON as opposed to hard-code markdown

---

### [6] Bugs
~~- B1: Web scraping for Yahoo Finance is restricted for certain stocks, needs updates to `WebScraper`~~
- B2: Monte Carlo Simulations' explanatory text faces caching issues
~~- B3: Web scraper is encountering issues with accessing information from Yahoo Finance, to look into it~~

---

### [7] Authors
- **[Xavier Boon Santimano](https://github.com/xavsant)** - Lead Developer
- **Fang-Yi Hsieh** - Monte Carlo Simulations Function
- **Ling King** - Monte Carlo Simulations Function
- **Nick Bernardini** - Black-Scholes-Merton Function
- **Cheng Wei Hern Martin** - Sentiment Analysis Function
