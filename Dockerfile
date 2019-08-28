### Stage 1: The frontend builder

FROM node:12.7.0 AS webpack

RUN mkdir /node_deps

COPY package.json /node_deps
COPY package-lock.json /node_deps
COPY webpack.config.js /node_deps
COPY dll/static /node_deps/static

WORKDIR /node_deps
RUN npm install
RUN npm run build

### Stage 2: The release image

FROM python:3.7-slim
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /usr/src/
RUN apt update \
    && apt install -y libpq-dev gcc python3-dev mime-support gettext libgettextpo-dev \
    && pip install -r /usr/src/requirements.txt \
    && apt purge -y gcc python3-dev \
    && apt autoremove -y --purge

RUN mkdir /code
WORKDIR /code

EXPOSE 80

COPY dll /code/dll
COPY manage.py /code
COPY --from=webpack /node_deps/static/dist /code/dll/static/dist
