# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app
ENV PYTHONPATH=/app

# Install Git and Git LFS for pulling LFS-tracked model files
RUN apt-get update && apt-get install -y git git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy .gitattributes to know which files are LFS-tracked
COPY .gitattributes /app/.gitattributes

# Copy models directory (if Git LFS files aren't pulled, this will copy pointers)
# We'll verify and handle this in the application code
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
