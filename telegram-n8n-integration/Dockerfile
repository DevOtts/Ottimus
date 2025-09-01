# Dockerfile - Container build configuration
# Telegram to n8n Integration - Docker Deployment

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy and install Python dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py discover_chats.py ./
COPY .env.example ./

# Create volume mount point for session persistence
# This directory will be mounted as a volume to persist session.session across container restarts
RUN mkdir -p /app/data

# Define volume mount point
VOLUME ["/app/data"]

# Expose no ports (this is a background worker, not a web service)

# Run the main application
CMD ["python", "main.py"]

