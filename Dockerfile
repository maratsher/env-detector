FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3-pip
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev libgl1-mesa-glx ffmpeg


COPY . /app
WORKDIR /app

RUN pip3 install numpy Cython

RUN pip3 install --no-cache-dir -r requirements.txt