# NVIDIA swamp
# FROM nvidia/cuda:10.2-base
# FROM nvcr.io/nvidia/tensorrt:20.03-py3 
FROM nvcr.io/nvidia/pytorch:21.02-py3


# Python swamp
#FROM python:3.8-slim-buster

RUN apt-get update
RUN apt-get install git curl vim gcc g++ -y
RUN pip install --upgrade pip
#RUN pip install torch torchvision torchaudio

# Project swamp
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN ls -la /usr/src/app
#RUN pip install -r /usr/src/app/requirements.txt

# Other swamp
RUN apt-get update ##[edited]
RUN apt-get install ffmpeg libsm6 libxext6 -y

#RUN pip3 install torch==1.7.1+cu110 torchvision==0.8.2+cu110 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install torch==1.8.0+cu111 torchvision==0.9.0+cu111 torchaudio==0.8.0 -f https://download.pytorch.org/whl/torch_stable.html


