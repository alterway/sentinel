FROM python:3.6-alpine

WORKDIR /opt

COPY sentinel sentinel
COPY setup.py .

RUN pip install -e . && rm setup.py 

ENV BACKEND="consul" \
    ORCHESTRATOR="swarm"

ENTRYPOINT ["sentinel"]