FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3-pip
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev libgl1-mesa-glx ffmpeg

RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -f UTF-8 en_US.UTF-8

ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8

COPY . /app
WORKDIR /app

RUN pip3 install numpy==1.19.4 Cython==3.0.8

RUN pip3 install --no-cache-dir -r requirements.txt