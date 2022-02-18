FROM python:3.9 AS base

ENV APP_HOME /app
ENV APP_WORKERS 2
ENV APP_THREADS 2
ENV PORT 8080

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

WORKDIR $APP_HOME
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt
CMD exec gunicorn --bind :$PORT --workers $APP_WORKERS --threads $APP_THREADS --timeout 300 sistem_skoring_pelatihan_microsoft.wsgi:application