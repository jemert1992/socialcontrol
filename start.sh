#!/bin/bash

# Start script for Social Control application
# This script sets up the environment and starts the application

echo "Starting Social Control application..."

# Create necessary directories if they don't exist
mkdir -p src/static/uploads
mkdir -p logs

# Set environment variables for production
export FLASK_ENV=production
export GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
export GUNICORN_BIND=${GUNICORN_BIND:-0.0.0.0:8000}
export GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}

# Install dependencies if requirements.txt is newer than the last install
if [ requirements.txt -nt .requirements_installed ] || [ ! -f .requirements_installed ]; then
    echo "Installing/updating dependencies..."
    pip install -r requirements.txt
    touch .requirements_installed
fi

# Start the application with gunicorn
echo "Starting gunicorn server..."
exec gunicorn src.main:app \
    --bind $GUNICORN_BIND \
    --workers $GUNICORN_WORKERS \
    --timeout $GUNICORN_TIMEOUT \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info
