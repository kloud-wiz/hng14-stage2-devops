# Stage 1: builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip==24.0 && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: final image
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY worker.py .
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import redis, os; r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=int(os.getenv('REDIS_PORT',6379)), password=os.getenv('REDIS_PASSWORD','')); r.ping()" || exit 1
CMD ["python", "worker.py"]
