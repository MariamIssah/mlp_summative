# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app
ENV PYTHONPATH=/app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy models (needed at build time)
COPY models /app/models

# Copy all application code
COPY . /app

# Copy and make start script executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn using start script (respects Railway PORT env var)
# Railway sets PORT automatically, fallback to 8000 for local dev
CMD ["/app/start.sh"]
