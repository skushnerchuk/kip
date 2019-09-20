FROM prom/prometheus:v2.12.0

ARG VERSION
ARG MAINTAINER

LABEL version=VERSION
LABEL maintainer=MAINTAINER

COPY prometheus.yml /etc/prometheus/
COPY alerts.yml /etc/prometheus/
