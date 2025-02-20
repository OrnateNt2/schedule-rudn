#!/bin/bash
set -e

# Останавливаем и удаляем старые контейнеры, если они есть
docker-compose down --volumes --remove-orphans

# Собираем образ без кэша
docker-compose build --no-cache

# Запускаем контейнеры в фоновом режиме
docker-compose up -d

echo "Контейнер запущен"
