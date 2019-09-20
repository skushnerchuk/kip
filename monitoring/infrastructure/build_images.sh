#!/usr/bin/env bash

set -e

MAINTAINER="Sergey Kushnerchuk"
ALERT_VERSION="0.1"
PROM_VERSION="0.1"

echo MAINTAINER: ${MAINTAINER}
echo ALERT_VERSION: ${ALERT_VERSION}
echo PROM_VERSION: ${PROM_VERSION}

docker build --build-arg VERSION="${ALERT_VERSION}" --build-arg MAINTAINER="${MAINTAINER}" \
             -t registry.sk-developer.ru/alertmanager:${ALERT_VERSION} \
             ./alertmanager

docker build --build-arg VERSION="${PROM_VERSION}" --build-arg MAINTAINER="${MAINTAINER}" \
            -t registry.sk-developer.ru/prometheus:${PROM_VERSION} \
            ./prometheus

docker push registry.sk-developer.ru/alertmanager:${ALERT_VERSION}
docker push registry.sk-developer.ru/prometheus:${PROM_VERSION}
