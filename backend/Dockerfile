# Dockerfile

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# ---------------------------------------------------
# System Packages
# ---------------------------------------------------

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    git \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------
# Python Dependencies
# ---------------------------------------------------

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# ---------------------------------------------------
# Project
# ---------------------------------------------------

COPY . .

# ---------------------------------------------------
# Static
# ---------------------------------------------------

RUN mkdir -p /app/staticfiles \
    && chmod -R 775 /app \
    && chmod -R 777 /app/staticfiles

# ---------------------------------------------------
# Entrypoint
# ---------------------------------------------------

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2"]