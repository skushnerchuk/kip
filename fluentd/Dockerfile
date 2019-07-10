FROM fluent/fluentd:v1.5-1

MAINTAINER Sergey Kushnerchuk

USER root

RUN apk add --no-cache --update --virtual .build-deps \
        sudo build-base ruby-dev \
 && sudo gem install fluent-plugin-elasticsearch  --no-rdoc --no-ri --version 1.9.5 \
 && sudo gem install fluent-plugin-grok-parser --no-rdoc --no-ri --version 1.0.0 \
 && sudo gem sources --clear-all \
 && apk del .build-deps \
 && rm -rf /home/fluent/.gem/ruby/2.5.0/cache/*.gem

COPY fluent.conf /fluentd/etc/
COPY entrypoint.sh /bin/

USER fluent
