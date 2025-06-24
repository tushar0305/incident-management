#!/bin/bash

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
sleep 30

# Create topics
podman exec incident-kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 3 \
    --topic alerts-incoming

podman exec incident-kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 3 \
    --topic alerts-processed

podman exec incident-kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 3 \
    --topic incidents-created

podman exec incident-kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 3 \
    --topic notifications-sent

podman exec incident-kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 3 \
    --topic escalations-triggered

echo "Topics created successfully!"

# List topics to verify
podman exec incident-kafka kafka-topics --list --bootstrap-server localhost:9092
