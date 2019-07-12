#!/usr/bin/env bash

docker build -t registry.sk-developer.ru/kip_handler_email:latest .
docker login registry.sk-developer.ru
docker push registry.sk-developer.ru/kip_handler_email:latest
docker logout registry.sk-developer.ru
