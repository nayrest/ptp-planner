# Базовый образ: Linux + Python 3.13, облегчённая версия
FROM python:3.13-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Не создавать .pyc и сразу выводить логи (а не копить в буфере)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Сначала только зависимости — Docker закэширует этот слой,
# и при изменении кода библиотеки не будут ставиться заново
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом код
COPY ptp/ ptp/
COPY static/ static/

EXPOSE 8000

# Docker сам будет проверять, жив ли сервис, — через твой /health
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"

# Команда запуска. 0.0.0.0 — слушать снаружи контейнера, а не только внутри
CMD ["uvicorn", "ptp.api:app", "--host", "0.0.0.0", "--port", "8000"]