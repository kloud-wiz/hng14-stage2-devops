# ─ Stage 1: builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies into a separate directory
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─ Stage 2: final image
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY main.py .

# Create non-root user and switch to it
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

# Expose the API port
EXPOSE 8000

# Health check — hits our /health endpoint every 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Start the API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]