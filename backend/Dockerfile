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

# Copy your application code
COPY api.py ./
COPY tasks/ ./
COPY models/ ./ 
# models/

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpython3-dev && rm -rf /var/lib/apt/lists/*
RUN python Setup.py build_ext --inplace

