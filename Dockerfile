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

RUN apt-get --assume-yes install curl

RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg

RUN mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg

RUN sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'

RUN apt-get --assume-yes install apt-transport-https ca-certificates 

RUN apt-get update && apt-get --assume-yes install azure-functions-core-tools

