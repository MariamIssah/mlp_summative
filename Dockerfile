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
# Use requirements-api.txt for API deployment (includes TensorFlow)
COPY requirements-api.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code (including models, data, scripts, etc.)
COPY . /app

# For Railway free tier: Skip training during build to avoid OOM errors
# Instead, use a pre-trained small model or train on first /retrain call
# If you have a small pre-trained model, it will be copied from models/ directory
RUN mkdir -p /app/models

# Optional: Uncomment below to train during build (may cause OOM on free tier)
# RUN export TF_CPP_MIN_LOG_LEVEL=2 && python scripts/train_small_model_for_railway.py

# Ensure start script is executable
RUN chmod +x /app/start.sh

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn using start script (respects Railway PORT env var)
# Railway sets PORT automatically, fallback to 8000 for local dev
CMD ["/app/start.sh"]
