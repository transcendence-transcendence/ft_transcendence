# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create and set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
# postgreSQL
    libpq-dev \
    build-essential \
# 임시 cache제거
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files and apply migrations
CMD sh -c "python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p 8080 ft_transcendence.asgi:application"
# migrate: Django DB 설정 update
# collectstatic --noinput: input없이 static파일을 한곳에 모아 nginx사용 용이하게 setting
# daphne -b 0.0.0.0 -p 8000 ft_transcendence.asgi:application: 웹소켓 비동기 처리 위한 ASGI 서버 모든 NIC서 8000번포트로 수신