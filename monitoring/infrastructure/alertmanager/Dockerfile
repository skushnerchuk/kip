FROM prom/alertmanager:v0.14.0

ARG VERSION
ARG MAINTAINER

LABEL version=VERSION
LABEL maintainer=MAINTAINER

COPY config.yml /etc/alertmanager/
