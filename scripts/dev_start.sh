#!/bin/bash

echo "🚀 Starting Incident Management Development Environment..."

# Stop any existing containers
echo "📦 Stopping existing containers..."
podman-compose -f containers/podman-compose.yml down

# Start all services
echo "🎯 Starting services..."
podman-compose -f containers/podman-compose.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Services are running:"
echo "   - PostgreSQL: localhost:5433"
echo "   - Kafka: localhost:9092"
echo "   - Kafka UI: http://localhost:8080"

echo ""
echo "🎉 Development environment is ready!"
echo "💡 Run 'python manage.py runserver' to start Django"
