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

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn (respect Railway/Heroku PORT env var)
# Railway sets PORT automatically, fallback to 8000 for local dev
CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
