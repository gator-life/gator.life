FROM python:2.7-slim

COPY trained_topic_model ./trained_topic_model

#https://www.bountysource.com/issues/25625672-cchardet-is-not-working-docker-python-slim
ENV BUILD_DEPS gcc g++ libffi-dev openssl libssl-dev
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
	&& apt-get install -y $BUILD_DEPS --no-install-recommends \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt

RUN pip install -U pip \
	&& pip install -r requirements.txt \
	&& python -m nltk.downloader stopwords \
	&& python -m nltk.downloader punkt \
		&& find /usr/local -depth \
		\( \
		    \( -type d -a -name test -o -name tests \) \
		    -o \
		    \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		\) -exec rm -rf '{}' + \
	&& rm -rf /usr/src/python ~/.cache \
	&& apt-get purge -y --auto-remove $BUILD_DEPS



