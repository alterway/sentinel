FROM python:3.6-alpine

RUN echo "http://dl-6.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk update || true \
    && apk add --no-cache docker \
    && mkdir -p /var/www/html

COPY sentinel /sentinel

RUN pip install docker

WORKDIR /sentinel

ENTRYPOINT ["python"]
CMD ["sentinel.py"]
