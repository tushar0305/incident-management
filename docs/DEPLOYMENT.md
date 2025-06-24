# 🚀 Deployment Guide

## Overview

This guide covers deploying the Incident Management System to production environments. The system can be deployed using various strategies from simple single-server deployments to complex multi-server architectures.

## 🏗️ Deployment Options

### 1. Single Server Deployment (Small Scale)
- All services on one server
- Suitable for small teams (< 50 users)
- Easy to manage and maintain

### 2. Multi-Server Deployment (Medium Scale)
- Separate database and application servers
- Load balancer for high availability
- Suitable for medium teams (50-500 users)

### 3. Container Orchestration (Large Scale)
- Kubernetes or Docker Swarm
- Auto-scaling and high availability
- Suitable for large organizations (500+ users)

## 🐳 Docker Deployment

### Prerequisites

- Docker 20.0+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Production Docker Setup

1. **Create production docker-compose.yml:**

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://incident_user:${DB_PASSWORD}@db:5432/incident_db
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - EMAIL_HOST=${EMAIL_HOST}
      - EMAIL_HOST_USER=${EMAIL_HOST_USER}
      - EMAIL_HOST_PASSWORD=${EMAIL_HOST_PASSWORD}
    depends_on:
      - db
      - kafka
    volumes:
      - static_volume:/app/static
      - media_volume:/app/media
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=incident_db
      - POSTGRES_USER=incident_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    restart: unless-stopped

  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    restart: unless-stopped

  consumer:
    build: .
    command: python manage.py consume_incidents
    environment:
      - DATABASE_URL=postgresql://incident_user:${DB_PASSWORD}@db:5432/incident_db
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
    depends_on:
      - db
      - kafka
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/static
      - media_volume:/app/media
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

2. **Create Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN useradd --create-home --shell /bin/bash incident
RUN chown -R incident:incident /app
USER incident

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "incident_management.wsgi:application"]
```

3. **Create .env file:**

```env
DB_PASSWORD=secure_password_here
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
SECRET_KEY=your-super-secure-secret-key
```

4. **Deploy:**

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster 1.20+
- kubectl configured
- Helm 3.0+ (optional)

### Kubernetes Manifests

1. **Namespace:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: incident-management
```

2. **ConfigMap:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: incident-config
  namespace: incident-management
data:
  DATABASE_URL: "postgresql://incident_user:password@postgres:5432/incident_db"
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  DEBUG: "False"
```

3. **Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: incident-web
  namespace: incident-management
spec:
  replicas: 3
  selector:
    matchLabels:
      app: incident-web
  template:
    metadata:
      labels:
        app: incident-web
    spec:
      containers:
      - name: web
        image: incident-management:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: incident-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

4. **Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: incident-web-service
  namespace: incident-management
spec:
  selector:
    app: incident-web
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## 🌐 Traditional Server Deployment

### Prerequisites

- Ubuntu 20.04+ or CentOS 8+
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Systemd

### Server Setup

1. **Install Dependencies:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# CentOS/RHEL
sudo yum update
sudo yum install python3 python3-pip nginx postgresql postgresql-server
```

2. **Setup PostgreSQL:**

```bash
# Initialize database
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE incident_db;
CREATE USER incident_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE incident_db TO incident_user;
\q
```

3. **Setup Application:**

```bash
# Create user
sudo useradd --create-home --shell /bin/bash incident
sudo su - incident

# Clone and setup
git clone https://github.com/your-org/incident-management.git
cd incident-management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production values

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

4. **Setup Gunicorn:**

```bash
# Create systemd service
sudo nano /etc/systemd/system/incident-web.service
```

```ini
[Unit]
Description=Incident Management Web Service
After=network.target

[Service]
User=incident
Group=incident
WorkingDirectory=/home/incident/incident-management
Environment="PATH=/home/incident/incident-management/venv/bin"
ExecStart=/home/incident/incident-management/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/incident/incident-management/incident.sock \
          incident_management.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Setup Kafka Consumer Service:**

```bash
sudo nano /etc/systemd/system/incident-consumer.service
```

```ini
[Unit]
Description=Incident Management Kafka Consumer
After=network.target

[Service]
User=incident
Group=incident
WorkingDirectory=/home/incident/incident-management
Environment="PATH=/home/incident/incident-management/venv/bin"
ExecStart=/home/incident/incident-management/venv/bin/python manage.py consume_incidents
Restart=always

[Install]
WantedBy=multi-user.target
```

6. **Setup Nginx:**

```bash
sudo nano /etc/nginx/sites-available/incident-management
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/incident/incident-management;
    }
    
    location /media/ {
        root /home/incident/incident-management;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/incident/incident-management/incident.sock;
    }
}
```

7. **Enable Services:**

```bash
sudo systemctl daemon-reload
sudo systemctl start incident-web
sudo systemctl enable incident-web
sudo systemctl start incident-consumer
sudo systemctl enable incident-consumer

sudo ln -s /etc/nginx/sites-available/incident-management /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Certificate

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... rest of configuration
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Production Settings

### Django Settings

Create `incident_management/settings/production.py`:

```python
from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'incident_db'),
        'USER': os.environ.get('DB_USER', 'incident_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'Incident Management <noreply@your-domain.com>'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/incident-management/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

## 📈 Monitoring & Logging

### Application Monitoring

1. **Sentry Integration:**

```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

2. **Health Check Endpoint:**

```python
# incidents/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

### Infrastructure Monitoring

1. **Prometheus + Grafana:**

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

2. **Log Aggregation:**

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
```

## 🔄 Backup & Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/incident-management"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h localhost -U incident_user incident_db > $BACKUP_DIR/incident_db_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "incident_db_*.sql" -mtime +7 -delete
```

### File Backup

```bash
#!/bin/bash
# backup-files.sh
rsync -av /home/incident/incident-management/media/ /backups/media/
rsync -av /home/incident/incident-management/static/ /backups/static/
```

### Automated Backup

```bash
# Add to crontab
0 2 * * * /home/incident/backup.sh
0 3 * * * /home/incident/backup-files.sh
```

## 🚀 Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_incident_status ON incidents_incident(status);
CREATE INDEX idx_incident_priority ON incidents_incident(priority);
CREATE INDEX idx_incident_created_at ON incidents_incident(created_at);
CREATE INDEX idx_incident_assigned_to ON incidents_incident(assigned_to_id);
```

### Caching

```python
# settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache middleware
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    # ... other middleware
    'django.middleware.cache.FetchFromCacheMiddleware',
]

CACHE_MIDDLEWARE_SECONDS = 300
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Errors:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
# Check connection
psql -h localhost -U incident_user -d incident_db
```

2. **Kafka Connection Issues:**
```bash
# Check Kafka topics
kafka-topics --list --bootstrap-server localhost:9092
# Check consumer groups
kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

3. **Static Files Not Loading:**
```bash
# Collect static files
python manage.py collectstatic --noinput
# Check Nginx configuration
sudo nginx -t
```

### Log Locations

- **Django Logs:** `/var/log/incident-management/django.log`
- **Nginx Logs:** `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **PostgreSQL Logs:** `/var/log/postgresql/postgresql-*.log`
- **Systemd Services:** `journalctl -u incident-web -f`

---

This deployment guide provides comprehensive instructions for various deployment scenarios. Choose the approach that best fits your infrastructure and scaling requirements. 