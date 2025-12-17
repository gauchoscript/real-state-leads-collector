# Use Python 3.11 Alpine image as base
FROM python:3.11-alpine

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN adduser -D -u 1000 collector && \
    chown -R collector:collector /app

# Switch to non-root user
USER collector
