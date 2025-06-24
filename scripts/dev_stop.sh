#!/bin/bash

echo "Stopping Incident Management Backend Development Environment..."

cd containers
podman-compose down

echo "✅ All services stopped!"
