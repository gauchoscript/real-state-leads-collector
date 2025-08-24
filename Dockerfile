# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m -u 1000 scraper && \
    chown -R scraper:scraper /app

# Switch to non-root user
USER scraper
