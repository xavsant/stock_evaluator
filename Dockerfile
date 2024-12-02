# Specify version
FROM python:3.11.9-bullseye

# Create directories
WORKDIR /code

# Copy entire 'backend' directory
COPY ./backend /code/backend

# Copy dependencies
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Download NLTK stopwords
RUN python -m nltk.downloader stopwords punkt_tab wordnet

EXPOSE 80

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "80"]