FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# One worker + threads: the FAISS index is cached per process, so extra workers would each re-embed.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn project.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 8 --timeout 180"]
