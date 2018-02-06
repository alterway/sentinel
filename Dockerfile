FROM python:3.6-alpine

RUN echo "http://dl-6.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk update || true \
    && apk add --no-cache docker \
    && mkdir -p /var/www/html

WORKDIR /usr/local/lib/python3.6/site-packages
COPY sentinel sentinel
COPY setup.py .

RUN pip install -e .

ENV BACKEND consul
ENV ORCHESTRATOR swarm

ENTRYPOINT ["sentinel"]
