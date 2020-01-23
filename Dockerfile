FROM python:3.6-slim

# see output in our console 
ENV PYTHONUNBUFFERED 1
ARG CONFIG 

COPY requirements.txt /requirements.txt
COPY docker/requirements/$CONFIG.txt /requirements.$CONFIG.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev apt-utils\
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir -r /requirements.$CONFIG.txt \
    && apt-get purge -y --auto-remove gcc python3-dev apt-utils

RUN mkdir /code
WORKDIR /code

COPY . /code/