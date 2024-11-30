## Stock Evaluator

Index:
[1] Description
[2] Structure
[3] Dependencies
[4] Running the project
[5] ToDo

#### [1] Description

Web Application for Portfolio Stock Evaluation using Monte Carlo Simulations, Black-Scholes-Merton Model for Stock Options, and Sentiment Analysis.

#### [2] Structure
```
stock_evaluator/
│
├── app.py                      # Streamlit app with options to select analysis and view results
│
├── backend/
│   ├── __init__.py             # Initialise backend packages
│   ├── black_scholes_merton.py
│   ├── monte_carlo.py
│   ├── sentiment_analysis.py  
│   ├── main.py                 # FastAPI app with endpoints for each analysis    
│   ├── utils/                  # Helper functions
│   │   ├── __init__.py
│   │   └── data_fetching.py    # Functions to fetch stock data from Yahoo Finance
│   └── models/     
│       ├── __init__.py            
│       └── sentiment_model.py        
│
├── streamlit/                  # Streamlit pages
│   ├── black_scholes_merton_app.py
│   ├── monte_carlo_app.py
│   └── sentiment_analysis_app.py  
│
├── notebooks/
│   └── ...                     # For feature experimentation
├── Dockerfile_frontend
├── Dockerfile_backend
├── requirements.txt            # Dependencies
└── README.md
```

#### [3] Dependencies

- python = "^3.11"
- [pandas](https://pypi.org/project/pandas/)
- [streamlit](https://pypi.org/project/streamlit/)
- [fastapi](https://pypi.org/project/fastapi/)

#### [4] Running the project

If any packages/dependencies are updated via poetry, be sure to export the requirements.txt using the following:
`poetry export --without-hashes -f requirements.txt -o requirements.txt`

For the end-state, imports of modules within the project are done using absolute filepaths. This is because of the nature of fastapi. To run specific files in isolation you will have to edit the imports (i.e. from backend.utils.data_fetching import WebScraper becomes from utils import Webscraper).

**Live version:**
WIP.
*Note: Ensure your IP has been given access to use the live versions*

**Locally with Docker:**
1. Run `docker build -t image_name -f Dockerfile_name .` in your command line
2. Run `docker run -p 0.0.0.0:80:80 image_name` for backend, `docker run -p 8501:8501 image_name` for frontend in your command line
3. Open up `0.0.0.0:80/docs` for backend, `0.0.0.0:8501` for frontend in your browser  
---
***Locally without Docker***
1. Frontend: Run `streamlit run app.py` in your command line
2. Backend: Run `fastapi run backend/main.py` in your command line
    API Docs: [For interactively testing backend functions](http://0.0.0.0:8000/docs)

#### [5] ToDo
- Make BSM variable names more comprehensive
- Extract current price from stock for BSM
- Add error handling for incorrect input values in streamlit
- Beautify BSM plot
- Add caching for each frontend function
- Fix Selenium and Docker issues
- Update input and output hinting for class functions
- Update dependencies in README
- Add documentation to classes
- Add comments to classes
- Fix class names in __init__ 
- Only use pickle for models, use JSON for dict