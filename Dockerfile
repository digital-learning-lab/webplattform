FROM node:12.7.0-alpine
RUN mkdir /deps
WORKDIR /deps
COPY package.json /deps
COPY package-lock.json /deps
RUN npm install


FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/