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

# Train a minimal model during build (optimized for Railway free tier)
# This ensures a model is available for predictions
# If training fails due to memory, the build will continue and model can be trained via /retrain
RUN mkdir -p /app/models && \
    if [ -f "models/best_model.h5" ]; then \
        echo "Using existing model file from repository"; \
        cp models/best_model.h5 /app/models/best_model.h5 || true; \
    else \
        echo "No existing model found, training new minimal model..."; \
        export TF_CPP_MIN_LOG_LEVEL=2 && \
        export TF_FORCE_GPU_ALLOW_GROWTH=true && \
        python scripts/train_small_model_for_railway.py && \
        echo "Model training completed successfully" || \
        echo "WARNING: Model training failed during build - model will need to be trained via /retrain endpoint"; \
    fi

# Ensure start script is executable
RUN chmod +x /app/start.sh

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn using start script (respects Railway PORT env var)
# Railway sets PORT automatically, fallback to 8000 for local dev
CMD ["/app/start.sh"]
