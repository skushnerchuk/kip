#!/usr/bin/env bash

set -e

VERSION="0.4"
MAINTAINER="Sergey Kushnerchuk"

echo ${VERSION}
echo ${MAINTAINER}


docker build --build-arg VERSION="${VERSION}" --build-arg MAINTAINER="${MAINTAINER}" \
             -t registry.sk-developer.ru/kip_backend:latest \
             -t registry.sk-developer.ru/kip_backend:${VERSION} \
             .

docker login registry.sk-developer.ru
docker push registry.sk-developer.ru/kip_backend:latest
docker push registry.sk-developer.ru/kip_backend:${VERSION}
