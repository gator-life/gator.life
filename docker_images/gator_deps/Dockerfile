FROM python:2.7

ENV DEBIAN_FRONTEND noninteractive

COPY trained_topic_model ./trained_topic_model
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
	&& rm -rf /usr/src/python ~/.cache



