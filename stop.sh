#!/bin/bash
set -e

docker-compose down --volumes --remove-orphans

echo "Контейнер остановлен и удалён"
