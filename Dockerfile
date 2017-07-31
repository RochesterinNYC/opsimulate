FROM python:2.7

RUN pip install opsimulate

RUN opsimulate setup

COPY sample-modules /tmp/sample-modules
