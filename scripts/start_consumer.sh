#!/bin/bash

echo "🚀 Starting Incident Management Kafka Consumer..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run from the project root directory."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Set Django settings module
export DJANGO_SETTINGS_MODULE=incident_management.settings

# Start the consumer
echo "📡 Starting Kafka consumer for incident events..."
python manage.py consume_incidents --log-level=INFO

echo "✅ Kafka consumer stopped." 