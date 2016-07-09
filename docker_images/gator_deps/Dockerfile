FROM python:2.7-slim

#https://www.bountysource.com/issues/25625672-cchardet-is-not-working-docker-python-slim
ENV BUILD_DEPS gcc g++ openssl libssl-dev libffi-dev
RUN apt-get update && apt-get install -y $BUILD_DEPS --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader punkt

RUN apt-get purge -y --auto-remove $BUILD_DEPS