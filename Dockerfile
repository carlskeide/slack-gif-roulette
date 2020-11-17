FROM python:3.6-alpine

RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    python3-dev

# App settings
ENV PYTHONPATH "/srv"
EXPOSE 3031 8080

RUN adduser -D app &&\
    mkdir -p /srv/app

# Setup python env
COPY ./requirements.txt /
RUN pip install --quiet --no-cache-dir --upgrade \
    -r /requirements.txt

# Copy source
COPY ./uwsgi.ini /
COPY ./src /srv/app

# Invocation
WORKDIR /srv/app
USER app
CMD ["/usr/local/bin/uwsgi", "/uwsgi.ini"]
