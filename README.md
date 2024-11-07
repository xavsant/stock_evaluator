## Stock Evaluator

Index:
[1] Description
[2] Structure
[3] Dependencies
[4] Running the project
[5] ToDo

#### [1] Description

Web Application for Stock Evaluation using Monte Carlo Simulations, Black-Scholes-Merton Model for Stock Options, and Sentiment Analysis.

#### [2] Structure

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
├── notebooks/
│   └── ...                     # For feature experimentation
├── Dockerfile_frontend
├── Dockerfile_backend
├── requirements.txt            # Dependencies
└── README.md                   # Documentation on how to set up and run the app

#### [3] Dependencies

- python = "^3.11"
- [pandas](https://pypi.org/project/pandas/)
- [streamlit](https://pypi.org/project/streamlit/)
- [fastapi](https://pypi.org/project/fastapi/)

#### [4] Running the project

If any packages/dependencies are updated via poetry, be sure to export the requirements.txt using the following:
`poetry export --without-hashes -f requirements.txt -o requirements.txt`

**Live version:**
WIP.
*Note: Ensure your IP has been given access to use the live versions*

**Locally with Docker:**
1. Run `docker build -t image_name -f Dockerfile_name .` in your command line
2. Run `docker run --env-file .env -p 0.0.0.0:80:80 image_name` for backend, `docker run -p 8501:8501 image_name` for frontend in your command line
3. Open up `0.0.0.0:80/docs` for backend, `0.0.0.0:8501` for frontend in your browser  
---
***Locally without Docker***
1. Frontend: Run `streamlit run app.py` in your command line
2. Backend: Run `fastapi run backend/main.py` in your command line
    API Docs: [For interactively testing backend functions](http://0.0.0.0:8000/docs)

#### [5] ToDo
To add.