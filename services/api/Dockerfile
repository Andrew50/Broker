FROM python:3.10.1-bullseye

# Set the working directory to /app
WORKDIR /app

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set environment variables
ENV AM_I_IN_A_DOCKER_CONTAINER Yes
ENV C_INCLUDE_PATH=/usr/local/lib/python3.10/site-packages/numpy/core/include:$C_INCLUDE_PATH
ENV PYTHONPATH=/app

# Install system dependencies for Python, Firefox, and GeckoDriver
RUN apt-get update \
    && apt-get install -y wget gnupg firefox-esr gcc libpython3-dev \
    && wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz \
    && tar -zxf geckodriver-v0.29.0-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-v0.29.0-linux64.tar.gz \
    && rm -rf /var/lib/apt/lists/*

# Copy your application code
COPY api.py ./
COPY async_Data.py ./
