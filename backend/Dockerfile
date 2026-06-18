# =====================================================================
# UDMS Backend — Multi-stage Dockerfile
# Stage 1: Build/install dependencies
# Stage 2: Lean production image
# =====================================================================

# ─── Stage 1: Builder ────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ─── Stage 2: Runtime ────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r udms && useradd -r -g udms -m udms

# Working directory
WORKDIR /app

# Copy application code
COPY --chown=udms:udms . .

# Create runtime directories
RUN mkdir -p uploads/avatars logs && chown -R udms:udms uploads logs

# Switch to non-root user
USER udms

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]
