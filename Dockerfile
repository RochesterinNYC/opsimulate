FROM python:2.7

ENV GOOGLE_APPLICATION_CREDENTIALS=/root/.opsimulate/service-account.json

RUN pip install opsimulate

RUN opsimulate setup
