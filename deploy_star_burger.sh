#!/usr/bin/env bash
set -e

BOLD="\033[1m"
BOLD_END="\033[0m"

cd /opt/star-burger/

echo -e "\n${BOLD}Загрузка изменений из репозитория...${BOLD_END}"
git pull

COMMIT=`git rev-parse --short HEAD`

echo -e "\n${BOLD}Установка библиотек для Python...${BOLD_END}"
source venv/bin/activate
pip install -r requirements.txt

echo -e "\n${BOLD}Установка библиотек для Node.js...${BOLD_END}"
npm install --only=dev

echo -e "\n${BOLD}Сборка фронтенда...${BOLD_END}"
parcel build bundles-src/index.js -d bundles --no-minify --public-url="./"

echo -e "\n${BOLD}Сборка статики Django...${BOLD_END}"
yes yes | venv/bin/python manage.py collectstatic --no-input

echo -e "\n${BOLD}Применение миграций...${BOLD_END}"
venv/bin/python manage.py migrate --no-input

echo -e "\n${BOLD}Перезапуск сервисов Systemd...${BOLD_END}"
systemctl restart starburger.service
systemctl reload nginx.service

echo -e "\n${BOLD}Отправка уведомления в Rollbar...${BOLD_END}"
curl -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "'$ROLLBAR_ENVIRONMENT'", "revision": "'$COMMIT'", "local_username": "'$USER'", "status": "succeeded"}'

echo -e "\n${BOLD}Деплой проекта успешно завершён!${BOLD_END}"