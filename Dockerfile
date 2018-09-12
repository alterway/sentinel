FROM python:3.6-alpine

WORKDIR /opt

COPY sentinel sentinel
COPY setup.py setup.py

RUN pip install -e . 

ENV BACKEND="consul" \
    ORCHESTRATOR="swarm"

ENTRYPOINT ["python", "/opt/sentinel"]