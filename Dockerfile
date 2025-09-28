# Multi-stage Dockerfile for Healthcare Community Platform
# Supports both development and production environments

# Stage 1: Base image with Python and Node.js
FROM node:18-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    build-base \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    git

# Set working directory
WORKDIR /app

# Stage 2: Python dependencies
FROM base AS python-deps

# Copy Python requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir -r requirements_migration.txt

# Stage 3: Node.js dependencies
FROM base AS node-deps

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Stage 4: Frontend build
FROM node-deps AS frontend-build

# Copy source code
COPY . .

# Build frontend
RUN npm run build

# Stage 5: Production image
FROM python:3.11-slim AS production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY --from=python-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-deps /usr/local/bin /usr/local/bin

# Copy Node.js dependencies and built frontend
COPY --from=node-deps /app/node_modules ./node_modules
COPY --from=frontend-build /app/.next ./.next
COPY --from=frontend-build /app/public ./public
COPY --from=frontend-build /app/package*.json ./

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/backups

# Set permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "app_unified.py"]