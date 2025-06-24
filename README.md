# 🚨 Incident Management System

A comprehensive Django-based incident management system with real-time event processing using Kafka. This system enables organizations to track, manage, and resolve incidents efficiently with automated notifications and escalation workflows.

## ✨ Features

- **📋 Incident Management**: Create, update, and track incidents with detailed information
- **🔄 Real-time Processing**: Kafka-based event streaming for instant notifications
- **📧 Automated Notifications**: Email alerts for incident creation and status updates
- **⚡ Smart Escalation**: Automatic escalation for high-priority incidents
- **📊 Dashboard & Analytics**: Visual dashboard with incident statistics
- **👥 User Management**: Role-based access with assignment capabilities
- **📎 File Attachments**: Upload and manage incident-related files
- **💬 Comments System**: Collaborative incident resolution with comments
- **🔍 Advanced Filtering**: Search and filter incidents by status, priority, category

## 🏗️ Architecture

```
┌─────────────────┐    HTTP Requests    ┌─────────────────┐
│   Web Browser   │ ◄─────────────────► │  Django Web App │
└─────────────────┘                     └─────────────────┘
                                                   │
                                                   │ Database
                                                   ▼
                                        ┌─────────────────┐
                                        │   PostgreSQL    │
                                        └─────────────────┘
                                                   │
                                                   │ Events
                                                   ▼
┌─────────────────┐    Kafka Events     ┌─────────────────┐
│ Kafka Consumer  │ ◄───────────────────│ Kafka Cluster   │
│                 │                     │                 │
│ • Notifications │                     │ • Zookeeper     │
│ • Escalations   │                     │ • Topics        │
│ • Workflows     │                     │ • Partitions    │
└─────────────────┘                     └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Podman or Docker
- PostgreSQL client tools (optional)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd incident-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Infrastructure Services

```bash
# Start PostgreSQL and Kafka
./scripts/dev_start.sh
```

This will start:
- PostgreSQL on port 5433
- Kafka on port 9092
- Kafka UI on http://localhost:8080

### 3. Setup Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

### 4. Start Django Application

```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

### 5. Start Kafka Consumer (Optional)

For real-time event processing:

```bash
# In a new terminal
./scripts/start_consumer.sh
```

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Detailed system architecture
- **[API Documentation](docs/API.md)** - REST API endpoints and usage
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Kafka Consumer Guide](KAFKA_CONSUMER_GUIDE.md)** - Event processing documentation
- **[Development Guide](docs/DEVELOPMENT.md)** - Development setup and guidelines

## 🛠️ Technology Stack

### Backend
- **Django 5.2.3** - Web framework
- **PostgreSQL** - Primary database
- **Kafka** - Event streaming platform
- **Django REST Framework** - API development

### Frontend
- **Bootstrap 5** - UI framework
- **HTML/CSS/JavaScript** - Frontend technologies

### Infrastructure
- **Podman/Docker** - Containerization
- **Zookeeper** - Kafka coordination
- **Kafka UI** - Kafka management interface

## 📊 Project Structure

```
incident-management/
├── docs/                       # Documentation
├── incident_management/        # Django project settings
├── incidents/                  # Main application
│   ├── models.py              # Data models
│   ├── views.py               # View controllers
│   ├── forms.py               # Django forms
│   ├── kafka_producer.py      # Kafka event producer
│   ├── kafka_consumer.py      # Kafka event consumer
│   └── management/commands/   # Management commands
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
├── containers/                 # Container configurations
├── scripts/                    # Utility scripts
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://incident_user:incident_pass@localhost:5433/incident_db
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration

The system uses PostgreSQL by default. Configuration is in `incident_management/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'incident_db',
        'USER': 'incident_user',
        'PASSWORD': 'incident_pass',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}
```

## 🎯 Usage Examples

### Creating an Incident

```python
from incidents.models import Incident

incident = Incident.objects.create(
    title="Server Outage",
    description="Production server is down",
    priority="high",
    category="hardware",
    reported_by=user
)
```

### API Usage

```bash
# Get all incidents
curl -X GET http://localhost:8000/api/incidents/

# Create new incident
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Content-Type: application/json" \
  -d '{"title": "New Issue", "priority": "medium"}'
```

## 📈 Monitoring

### Kafka Monitoring

- **Kafka UI**: http://localhost:8080
- **Consumer Lag**: Monitor in Kafka UI
- **Topic Health**: Check topic partitions and replicas

### Application Monitoring

- **Django Admin**: http://localhost:8000/admin/
- **Logs**: Check console output for application logs
- **Database**: Monitor PostgreSQL connections and queries

## 🔒 Security

- CSRF protection enabled
- User authentication required
- Role-based access control
- File upload validation
- SQL injection protection via Django ORM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the `docs/` folder for detailed guides

## 🎉 Acknowledgments

- Django community for the excellent web framework
- Apache Kafka for reliable event streaming
- Bootstrap team for the responsive UI framework
- All contributors who helped build this system
