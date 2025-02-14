# Используем официальный образ Python
FROM python:3.10

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY . .

# Запускаем бота
CMD ["python", "main.py"]
