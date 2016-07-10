FROM python:2.7-slim

COPY requirements.txt ./requirements.txt

#https://www.bountysource.com/issues/25625672-cchardet-is-not-working-docker-python-slim
ENV BUILD_DEPS gcc g++ openssl libssl-dev libffi-dev
RUN apt-get update && apt-get install -y $BUILD_DEPS --no-install-recommends && rm -rf /var/lib/apt/lists/* \
	&& pip install -r requirements.txt \
	&& python -m nltk.downloader stopwords \
	&& python -m nltk.downloader punkt \

		&& find /usr/local -depth \
		\( \
		    \( -type d -a -name test -o -name tests \) \
		    -o \
		    \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		\) -exec rm -rf '{}' + \
	&& apt-get purge -y --auto-remove $BUILD_DEPS \
	&& rm -rf /usr/src/python ~/.cache



