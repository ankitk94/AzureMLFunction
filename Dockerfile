FROM ubuntu:16.04

RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv

# update pip
RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

RUN alias python='/usr/bin/python3.6'

RUN apt-get update && apt-get --assume-yes install git && apt-get --assume-yes install gcc && apt-get --assume-yes install gzip

COPY requirements.txt /tmp

RUN cd /tmp && pip install -r requirements.txt

WORKDIR /home/ankhokha/

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1

RUN alias python='/usr/bin/python3.6'
