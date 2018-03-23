FROM python:3.6-alpine

WORKDIR /usr/local/lib/python3.6/site-packages
COPY sentinel sentinel
COPY setup.py .

RUN pip install -e . && rm setup.py

ENV BACKEND="consul" \
    ORCHESTRATOR="swarm"

ENTRYPOINT ["sentinel"]
