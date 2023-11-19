FROM python:3.10.1-bullseye
WORKDIR /home/myproj
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV AM_I_IN_A_DOCKER_CONTAINER Yes
COPY api.py ./
COPY worker.py ./
COPY tasks/ tasks
RUN apt-get update && apt-get install -y gcc libpython3-dev && rm -rf /var/lib/apt/lists/*
ENV C_INCLUDE_PATH=/usr/local/lib/python3.10/site-packages/numpy/core/include:$C_INCLUDE_PATH
WORKDIR /home/myproj/tasks
RUN python Setup.py build_ext --inplace