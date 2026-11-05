FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/securetask.sqlite3

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && mkdir -p /data \
    && chown app:app /data

COPY --chown=app:app app.py ./
COPY --chown=app:app templates ./templates

USER app
EXPOSE 5000
VOLUME ["/data"]

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]