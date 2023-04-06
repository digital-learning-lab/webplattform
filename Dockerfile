### Stage 1: The frontend builder

FROM node:12.22.12 AS webpack

RUN mkdir /node_deps

COPY package.json /node_deps
COPY package-lock.json /node_deps
COPY webpack.config.js /node_deps
COPY dll/static /node_deps/static

WORKDIR /node_deps
RUN npm install
RUN npm run build

### Stage 2: The release image

FROM python:3.10.9-slim as python_build
ENV PYTHONUNBUFFERED=1 \
	POETRY_VIRTUALENVS_CREATE=false \
	POETRY_CACHE_DIR='/var/cache/pypoetry'

COPY pyproject.toml poetry.lock /code/dll/
RUN apt update \
    && apt install -y libpq-dev gcc git python3-dev mime-support gettext libgettextpo-dev optipng jpegoptim \
    && pip install poetry \
		&& cd /code/dll && poetry install --no-dev \
		&& rm -rf "$POETRY_CACHE_DIR" \
    && apt purge -y gcc python3-dev \
    && apt autoremove -y --purge

ARG DJANGO_SECRET_KEY=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG DATABASE_NAME=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG DATABASE_USER=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG DATABASE_PASSWORD=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG DATABASE_HOST=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG CONTACT_EMAIL_BSB=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG CONTACT_EMAIL_DLL=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG SOLR_HOSTNAME=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG META_SITE_PROTOCOL=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG EMAIL_SENDER=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG REDIS_HOSTNAME=ThisIsJustHereSoWeCanRunManagementCommandsDuringBuild
ARG CELERY_TASK_ALWAYS_EAGER=1
ARG EMAIL_PORT=1

WORKDIR /code

EXPOSE 80

COPY dll /code/dll
COPY solr /code/solr
COPY manage.py /code
RUN cd /code && python manage.py compilemessages
COPY .coveragerc /code
COPY --from=webpack /node_deps/static/dist /code/dll/static/dist
