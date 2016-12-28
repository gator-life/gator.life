FROM ubuntu:16.04
MAINTAINER Gator life "https://github.com/gator-life/gator.life"

RUN apt-get update && \
    apt-get -y install default-jre git libffi-dev libopenblas-dev libssl-dev python-dev python-pip wget && \
    pip install virtualenv

RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    tar xvfj phantomjs-2.1.1-linux-x86_64.tar.bz2 && \
    rm phantomjs-2.1.1-linux-x86_64.tar.bz2
ENV PATH $PWD/phantomjs-2.1.1-linux-x86_64/bin:$PATH

RUN git clone https://github.com/gator-life/gator.life.git /home/gator.life

WORKDIR /home/gator.life

RUN virtualenv global_env && \
    . global_env/bin/activate && \
    scripts/install_envs.sh
