#!/bin/bash
# Start script for Railway deployment
# Properly handles PORT environment variable

PORT=${PORT:-8000}
echo "Starting server on port $PORT"
exec uvicorn api.app:app --host 0.0.0.0 --port "$PORT"

