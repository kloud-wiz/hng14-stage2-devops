# ─ Stage 1: builder
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# ─ Stage 2: final image
FROM node:20-slim

WORKDIR /app

# Copy installed node_modules from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy application code
COPY app.js .
COPY views/ ./views/

# Create non-root user and switch to it
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

EXPOSE 3000

# Health check — hits our /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))" || exit 1

CMD ["node", "app.js"]
