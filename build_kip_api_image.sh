#!/usr/bin/env bash

set -e

VERSION=0.3

docker build -t registry.sk-developer.ru/kip_backend:latest \
             -t registry.sk-developer.ru/kip_backend:$VERSION \
             .

docker push registry.sk-developer.ru/kip_backend:latest
docker push registry.sk-developer.ru/kip_backend:$VERSION
