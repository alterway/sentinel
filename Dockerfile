FROM python:3.7-alpine

WORKDIR /opt

RUN apk --update add curl bash

COPY sentinel sentinel

RUN pip install -e sentinel/

ENV BACKEND="consul" \
    ORCHESTRATOR="swarm"

ENTRYPOINT ["sentinel"]