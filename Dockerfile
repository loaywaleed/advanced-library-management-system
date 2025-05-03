FROM python:3.12-slim-bookworm
# uv image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# no pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN which uv && uv --version

ADD . /app

WORKDIR /app
RUN uv sync --locked

RUN echo "Checking contents of /app/.venv/bin:" && \
    ls -la /app/.venv/bin || echo "/app/.venv/bin not found or empty"

# Install GDAL system libraries
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH"

RUN echo "Checking executables in PATH:" && \
    which python && \
    which gunicorn && \
    which celery || echo "Executables not found in PATH"

RUN python manage.py collectstatic --noinput


# CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
