[![Build Status](https://travis-ci.com/skushnerchuk/kip.svg?branch=master)](https://travis-ci.com/skushnerchuk/kip)

### API сервиса курсов (Django Rest Framework)

Для запуска проекта на машине должен быть установлен docker

Для разработки требуется python версии не ниже 3.6

<details>
<summary>Быстрый запуск</summary>

Проект состоит из шести контейнеров:
- **kip_api** - контейнер API
- **kip_db** - контейнер СУБД MariaDB
- **kip_nginx** - контейнер nginx
- **kip_fluentd** - контейнер FluentD для сбора  логов
- **kip_es** - контейнер elasticsearch
- **kip_kibana** - контейнер Kibana

Nginx был добавлен в проект в связи с тем, что сервис API запускается под GUnicorn,
который неспособен отдавать статические файлы, что приводит к порче ссылок на компоненты административной панели Django (например, css-стили), из-за чего она выглядит непрезентабельно.

Для упрощения я не стал делать отдельный Dockerfile для сборки своего nginx с копированием конфигурации непосредственно в контейнер, а просто сделал соответствующий маппинг в docker-compose.yml

Для запуска проекта выполните в его папке команды:
```bash
sudo sysctl -w vm.max_map_count=262144
docker-compose up -d --build
```
Первая команда нужна для корретного старта контейнера ElasticSearch.

Посмотрите, какой адрес назначен сервису kip_nginx:
```bash
docker ps -q | xargs docker inspect --format "{{ .Id }} - {{ .Name }} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
```

Перейдите по адресу
```
http://nginx_ip/admin
```
Данные для авторизации по умолчанию:
```
email: admin@admin.com
пароль: admin
```
Сервис может ответить не сразу, так как он ожидает полной инициализации контейнера СУБД.

Контейнеры **kip_fluentd, kip_kibana, kip_es** были добавлены для того, чтобы можно было централизованно просматривать и анализировать логи работы приложений.

Для просмотра логов перейдите по адресу:
```
http://kibana_ip:5601/
```
</details>

<details>
<summary>Разработка</summary>

Для выполнения разработки можно поднять отдельно сервер MySQL командой:

```bash
docker run -d --restart always -e MYSQL_ROOT_PASSWORD=12345 -v /path/to/data:/var/lib/mysql --name mysqlserver mariadb
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysqlserver
```

Полученный адрес указать в файле .env в переменной DB_HOST

По адресу http://nginx_ip/swagger/ доступно краткое описание API, которое будет детализироваться в процессе разработки

Для остановки и удаления всех контейнеров проекта выполните в его папке команду:
```bash
docker-compose down
```

Все данные сохранятся, если вы не удалите папку, которая монтируется в сервисе **database** в файле **docker-compose.yml**

Для управления тестовыми данными можно использовать команду:

```bash
$ python3 manage.py prepare_data
```
Для получения параметров команды выполните:
```bash
$ python3 manage.py prepare_data --help
```
Пример для добавления новых данных:
```bash
$ python3 manage.py prepare_data --fill --users 1 --categories 5 --courses 5 --groups 1 --lessons 10
```
Выполнение этой команды приведет к созданию 1 пользователя, 5 категорий, 5 курсов в каждой категории, 1 группе в каждом курсе и 10 уроков в каждой группе

Пример для удаления всех данных:
```bash
$ python3 manage.py prepare_data --clear
```

В настроящее время на приватном GitLab настроена и выполняется сборка образа и его отправка в Docker Hub.
Демо проекта доступно по адресу:

Админка:
```
https://kip.sk-developer.ru/admin/
```
API:
```
https://kip.sk-developer.ru/api/v1/
```
</details>
