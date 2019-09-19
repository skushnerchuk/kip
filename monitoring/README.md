## Мониторинг инфраструктуры и сервисов

Для организации мониторинга и оперативного оповещения о возникающих проблемах используются 
следующие инструменты:
* Prometheus
* Prometheus node exporter
* InfluxDB
* Zipkin
* Grafana
* Prometheus alert manager

### Быстрый запуск и остановка инфраструктуры мониторинга
Для запуска всех компонентов выполните команду:
```shell script
docker-compose up -d
```
Для остановки всех компонентов выполните команду:
```shell script
docker-compose down
```

### Контролируемые метрики и параметры

### Настройка компонентов мониторинга