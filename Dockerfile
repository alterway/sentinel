FROM python:3.6-alpine

WORKDIR /opt

COPY sentinel sentinel

RUN pip install -e sentinel/ 

ENV BACKEND="consul" \
    ORCHESTRATOR="swarm"

ENTRYPOINT ["sentinel"]