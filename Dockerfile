FROM nvcr.io/nvidia/l4t-base:r32.6.1

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y software-properties-common

RUN apt-get update && apt-get install -y python3-pip

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && locale-gen en_US.UTF-8

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

COPY . /app
WORKDIR /app

RUN pip3 install numpy Cython

RUN pip3 install --no-cache-dir -r requirements.txt