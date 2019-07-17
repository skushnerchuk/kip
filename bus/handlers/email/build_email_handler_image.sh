#!/usr/bin/env bash

# Лучшим решением будет преобразовать common в пакет, который
# будет устанавливаться через pip + requirements, а не копироваться при сборке образа
# Это будет сделано, но позднее
cp -r ./../../../common ./

docker build -t registry.sk-developer.ru/kip_handler_email:latest .
docker login registry.sk-developer.ru
docker push registry.sk-developer.ru/kip_handler_email:latest
docker logout registry.sk-developer.ru

rm -rf ./common
