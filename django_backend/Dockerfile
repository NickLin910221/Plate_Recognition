FROM python:3.10

ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD . /app

RUN apt-get update
RUN apt-get -qy full-upgrade
RUN apt-get install -qy curl
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN apt-get -y install docker
RUN pip install -r /app/requirements.txt