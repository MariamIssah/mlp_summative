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

# Ensure a model file exists - create dummy model as fallback
# This ensures predictions work even if training fails
RUN mkdir -p /app/models
RUN python scripts/create_dummy_model.py || echo "Dummy model creation failed"
RUN if [ -f "models/best_model.h5" ]; then \
        cp models/best_model.h5 /app/models/best_model.h5 && \
        echo "Model file copied to /app/models/"; \
    else \
        echo "No model file found, dummy model should be in /app/models/"; \
    fi
RUN ls -lh /app/models/ || echo "Models directory listing failed"

# Ensure start script is executable
RUN chmod +x /app/start.sh

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI with Uvicorn using start script (respects Railway PORT env var)
# Railway sets PORT automatically, fallback to 8000 for local dev
CMD ["/app/start.sh"]
