FROM node:22-bookworm-slim AS runtime

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /app/backend/requirements.txt

COPY . /app
WORKDIR /app/backend

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD sh -c 'uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}'