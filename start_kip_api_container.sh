#!/usr/bin/env sh

docker run -d \
-p 8000:8000 \
--restart always \
-e "RMQ_HOST=127.0.0.1" \
-e "RMQ_PORT=5672" \
-e "RMQ_USERNAME=guest" \
-e "RMQ_PASSWORD=guest" \
-e "DB_USER=kip" \
-e "DB_PASSWORD=VFERGUSON11284kip" \
-e "DB_HOST=192.168.1.14" \
-e "DB_PORT=3306" \
-e "DJANGO_SETTINGS_MODULE=kip.settings" \
-e "ACCESS_TOKEN_LIMIT=365" \
-e "REFRESH_TOKEN_LIMIT=1" \
-e "PORT=8000" \
registry.sk-developer.ru/kip_backend:latest kip_ap
