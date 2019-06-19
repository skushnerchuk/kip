[![Build Status](https://travis-ci.com/skushnerchuk/kip.svg?branch=master)](https://travis-ci.com/skushnerchuk/kip)

### API сервиса курсов (Django Rest Framework)

Для запуска проекта на машине должен быть установлен docker

Для разработки требуется python версии не ниже 3.6

#### Быстрый запуск.

Проект состоит из 3-х контейнеров:
- **kip_api** - контейнер API
- **kip_db** - контейнер СУБД MariaDB
- **kip_nginx** - контейнер nginx

Nginx был добавлен в проект в связи с тем, что сервис API запускается под GUnicorn, 
который неспособен отдавать статические файлы, что приводит к порче ссылок на компоненты административной панели Django (например, css-стили), из-за чего она выглядит непрезентабельно. 

Для упрощения я не стал делать отдельный Dockerfile для сборки своего nginx с копированием конфигурации непосредственно в контейнер, а просто сделал соответствующий маппинг в docker-compose.yml

Для запуска проекта выполните в его папке команду:
```bash
docker-compose up -d --build
```
Посмотрите, какой адрес назначен сервису kip_nginx:
```bash
docker ps -q | xargs docker inspect --format "{{ .Id }} - {{ .Name }} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
```

Перейдите по адресу
```
http://nginx_api/admin
```
Данные для авторизации по умолчанию:
```
email: admin@admin.com
пароль: admin
```
Сервис может ответить не сразу, так как он ожидает полной инициализации контейнера СУБД.

#### Разработка

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

Тестирование проекта планируется с помощью сервиса **travis-ci.com**
