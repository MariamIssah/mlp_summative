#!/bin/bash
# Start script for Railway deployment
# Properly handles PORT environment variable

PORT=${PORT:-8000}
echo "Starting server on port $PORT"
echo "Uvicorn will keep the service alive for Railway health checks"
# Use --timeout-keep-alive to keep connections alive for Railway
# Use --log-level info to ensure Railway sees activity
exec uvicorn api.app:app --host 0.0.0.0 --port "$PORT" --timeout-keep-alive 65 --log-level info

