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


# Copy the current directory contents into the container at /usr/src/app
COPY Database.py ./

# Install cron
RUN apt-get update && apt-get -y install cron

# Add crontab file in the cron directory
COPY crontab /etc/cron.d/my-cron-job

# Give execution rights on the cron job and script
RUN chmod 0644 /etc/cron.d/my-cron-job
RUN chmod +x ./Database.py

# Apply cron job
RUN crontab /etc/cron.d/my-cron-job

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log

