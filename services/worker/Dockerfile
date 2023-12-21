FROM python:3.10.1-bullseye
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER Yes
ENV C_INCLUDE_PATH=/usr/local/lib/python3.10/site-packages/numpy/core/include:$C_INCLUDE_PATH
ENV PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y wget gnupg firefox-esr gcc libpython3-dev \
    && wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz \
    && tar -zxf geckodriver-v0.29.0-linux64.tar.gz -C /usr/local/bin \
    && rm geckodriver-v0.29.0-linux64.tar.gz \
    && rm -rf /var/lib/apt/lists/*

RUN python Setup.py build_ext --inplace
CMD ["/bin/sh", "-c", "sleep 5 && rq worker --url redis://redis-service:6379 my_queue"]