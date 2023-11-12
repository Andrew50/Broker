#FROM python:3.7.6
FROM python:3.10.1

WORKDIR /home/myproj


RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY api.py ./
COPY worker.py ./
COPY tasks/ tasks
COPY Setup.py ./


#RUN python Setup.py build_ext --inplace
