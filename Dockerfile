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

# Ensure a model file exists - try multiple approaches
RUN mkdir -p /app/models && \
    if [ -f "models/best_model.h5" ] && [ -s "models/best_model.h5" ]; then \
        echo "Using existing model file from repository"; \
        cp models/best_model.h5 /app/models/best_model.h5 && \
        echo "Model copied successfully"; \
    elif [ -d "data/train_min" ] && [ "$(ls -A data/train_min 2>/dev/null)" ]; then \
        echo "Training data found, training minimal model..."; \
        export TF_CPP_MIN_LOG_LEVEL=2 && \
        export TF_FORCE_GPU_ALLOW_GROWTH=true && \
        python scripts/train_small_model_for_railway.py && \
        cp models/best_model.h5 /app/models/best_model.h5 && \
        echo "Model trained and copied successfully" || \
        (echo "Training failed, creating dummy model..." && \
         python scripts/create_dummy_model.py && \
         cp models/best_model.h5 /app/models/best_model.h5 && \
         echo "Dummy model created as fallback"); \
    else \
        echo "No training data found, creating dummy model..."; \
        python scripts/create_dummy_model.py && \
        cp models/best_model.h5 /app/models/best_model.h5 && \
        echo "Dummy model created - use /retrain to train proper model"; \
    fi && \
    ls -lh /app/models/ && \
    echo "Model setup complete"

# Ensure start script is executable
RUN chmod +x /app/start.sh

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn using start script (respects Railway PORT env var)
# Railway sets PORT automatically, fallback to 8000 for local dev
CMD ["/app/start.sh"]
