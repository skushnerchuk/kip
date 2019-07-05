FROM python:3.7-alpine

ARG VERSION
ARG MAINTAINER

LABEL version=$VERSION
LABEL maintainer=$MAINTAINER

WORKDIR /app

COPY requirements.txt /app
RUN echo "http://mirror.leaseweb.com/alpine/edge/testing" >> /etc/apk/repositories \
    && apk update \
    && apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers bash \
            python3-dev libgcc libstdc++ musl geos-dev libxml2-dev libxslt-dev \
            mariadb-dev libffi libffi-dev gmp-dev mpfr-dev bash jq curl \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del --no-cache --purge .build-deps \
    && rm -rf /var/cache/apk/*

RUN apk add --no-cache mariadb-dev bash && rm -rf /var/cache/apk/*

COPY . /app
WORKDIR /app

COPY ./docker-entrypoint.sh /app/kip/
COPY ./wait-for-db.sh /app/kip/

ENTRYPOINT ["/app/kip/docker-entrypoint.sh"]
