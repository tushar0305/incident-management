# 🛠️ Development Guide

## Overview

This guide covers setting up the development environment, coding standards, testing procedures, and contribution guidelines for the Incident Management System.

## 🚀 Development Setup

### Prerequisites

- Python 3.8+ 
- Git
- Podman or Docker
- Code editor (VS Code recommended)

### Local Development Environment

1. **Clone the Repository:**

```bash
git clone https://github.com/your-org/incident-management.git
cd incident-management
```

2. **Setup Virtual Environment:**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

3. **Install Dependencies:**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Environment Configuration:**

```bash
# Copy environment template
cp .env.example .env

# Edit .env with development settings
DEBUG=True
SECRET_KEY=your-development-secret-key
DATABASE_URL=postgresql://incident_user:incident_pass@localhost:5433/incident_db
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

5. **Start Infrastructure Services:**

```bash
./scripts/dev_start.sh
```

6. **Setup Database:**

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json
```

7. **Start Development Server:**

```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

## 📁 Project Structure

```
incident-management/
├── docs/                           # Documentation
├── incident_management/            # Django project settings
│   ├── __init__.py
│   ├── settings.py                 # Main settings
│   ├── urls.py                     # URL routing
│   └── wsgi.py                     # WSGI configuration
├── incidents/                      # Main application
│   ├── __init__.py
│   ├── admin.py                    # Django admin
│   ├── apps.py                     # App configuration
│   ├── forms.py                    # Django forms
│   ├── kafka_consumer.py           # Kafka event consumer
│   ├── kafka_producer.py           # Kafka event producer
│   ├── models.py                   # Data models
│   ├── tests/                      # Test files
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_kafka.py
│   ├── urls.py                     # App URL routing
│   ├── views.py                    # View controllers
│   └── management/                 # Management commands
│       └── commands/
│           └── consume_incidents.py
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── registration/               # Auth templates
│   └── incidents/                  # App templates
├── static/                         # Static files
│   ├── css/                        # Stylesheets
│   ├── js/                         # JavaScript
│   └── images/                     # Images
├── containers/                     # Container configurations
│   └── podman-compose.yml
├── scripts/                        # Utility scripts
│   ├── dev_start.sh               # Start development services
│   └── start_consumer.sh          # Start Kafka consumer
├── fixtures/                       # Sample data
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Development dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project overview
└── manage.py                       # Django management script
```

## 🎨 Coding Standards

### Python Code Style

We follow **PEP 8** with some modifications:

- **Line Length**: 88 characters (Black formatter default)
- **Indentation**: 4 spaces
- **Imports**: Group and sort imports
- **Docstrings**: Use Google-style docstrings

### Code Formatting

We use **Black** for code formatting:

```bash
# Install Black
pip install black

# Format code
black .

# Check formatting
black --check .
```

### Import Organization

Use **isort** for import sorting:

```bash
# Install isort
pip install isort

# Sort imports
isort .

# Check import sorting
isort --check-only .
```

### Example Code Style

```python
"""
Module for handling incident operations.

This module contains views and utilities for managing incidents
in the incident management system.
"""

import json
import logging
from typing import Dict, List, Optional

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Incident
from .kafka_producer import send_incident_notification


logger = logging.getLogger(__name__)


class IncidentService:
    """Service class for incident operations."""
    
    def __init__(self):
        """Initialize the incident service."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_incident(self, title: str, description: str, priority: str) -> Incident:
        """
        Create a new incident.
        
        Args:
            title: The incident title
            description: Detailed description
            priority: Priority level (low, medium, high, critical)
            
        Returns:
            The created incident instance
            
        Raises:
            ValidationError: If the data is invalid
        """
        incident = Incident.objects.create(
            title=title,
            description=description,
            priority=priority
        )
        
        # Send notification
        try:
            send_incident_notification(incident)
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
        
        return incident
```

### Django Best Practices

1. **Models:**
   - Use descriptive field names
   - Add `__str__` methods
   - Use model validation
   - Add database indexes for frequently queried fields

2. **Views:**
   - Keep views thin, move logic to services/models
   - Use class-based views for complex logic
   - Add proper error handling
   - Use decorators for common functionality

3. **Templates:**
   - Use template inheritance
   - Keep logic minimal in templates
   - Use template tags for reusable components
   - Escape user input properly

4. **Forms:**
   - Use Django forms for validation
   - Add custom validation methods
   - Use widgets for better UX

## 🧪 Testing

### Test Structure

```
incidents/tests/
├── __init__.py
├── test_models.py          # Model tests
├── test_views.py           # View tests
├── test_forms.py           # Form tests
├── test_kafka.py           # Kafka integration tests
└── test_utils.py           # Utility function tests
```

### Writing Tests

```python
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from incidents.models import Incident


class IncidentModelTest(TestCase):
    """Test cases for Incident model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_incident_creation(self):
        """Test incident creation."""
        incident = Incident.objects.create(
            title='Test Incident',
            description='Test description',
            priority='medium',
            category='software',
            reported_by=self.user
        )
        
        self.assertEqual(incident.title, 'Test Incident')
        self.assertEqual(incident.status, 'open')
        self.assertEqual(incident.reported_by, self.user)
    
    def test_incident_str_representation(self):
        """Test string representation of incident."""
        incident = Incident.objects.create(
            title='Test Incident',
            description='Test description',
            priority='high',
            reported_by=self.user
        )
        
        self.assertEqual(str(incident), 'Test Incident')


class IncidentViewTest(TestCase):
    """Test cases for incident views."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_incident_list_view(self):
        """Test incident list view."""
        response = self.client.get(reverse('incidents:incident_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incidents')
    
    def test_incident_creation_view(self):
        """Test incident creation via POST."""
        data = {
            'title': 'New Incident',
            'description': 'Test description',
            'priority': 'high',
            'category': 'hardware'
        }
        
        response = self.client.post(reverse('incidents:create_incident'), data)
        
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Incident.objects.filter(title='New Incident').exists())
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test incidents

# Run specific test file
python manage.py test incidents.tests.test_models

# Run specific test method
python manage.py test incidents.tests.test_models.IncidentModelTest.test_incident_creation

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Database

Tests use a separate test database that's created and destroyed automatically.

## 🔧 Development Tools

### Recommended VS Code Extensions

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.flake8",
        "bradlc.vscode-tailwindcss",
        "ms-vscode.vscode-json",
        "redhat.vscode-yaml"
    ]
}
```

### VS Code Settings

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": false,
    "python.testing.nosetestsEnabled": false,
    "python.testing.djangoEnabled": true,
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.2.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## 🐛 Debugging

### Django Debug Toolbar

Install Django Debug Toolbar for development:

```bash
pip install django-debug-toolbar
```

Add to `settings.py`:

```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
```

### Logging Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'incidents': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Common Debugging Commands

```bash
# Django shell
python manage.py shell

# Database shell
python manage.py dbshell

# Show migrations
python manage.py showmigrations

# SQL for migration
python manage.py sqlmigrate incidents 0001

# Check for issues
python manage.py check

# Validate templates
python manage.py validate_templates
```

## 🔄 Development Workflow

### Git Workflow

We use **Git Flow** with the following branches:

- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `hotfix/*`: Hotfix branches
- `release/*`: Release branches

### Branch Naming

- `feature/incident-search`
- `bugfix/kafka-connection-error`
- `hotfix/security-patch`
- `docs/api-documentation`

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat(incidents): add search functionality

fix(kafka): resolve connection timeout issue

docs(api): update endpoint documentation

test(models): add incident model tests
```

### Pull Request Process

1. **Create Feature Branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes and Commit:**
```bash
git add .
git commit -m "feat(incidents): add new feature"
```

3. **Push Branch:**
```bash
git push origin feature/your-feature-name
```

4. **Create Pull Request:**
   - Use descriptive title
   - Add detailed description
   - Link related issues
   - Add screenshots if UI changes
   - Request code review

5. **Code Review:**
   - Address feedback
   - Update code as needed
   - Ensure tests pass

6. **Merge:**
   - Squash commits if needed
   - Delete feature branch

## 📦 Dependencies Management

### Adding New Dependencies

1. **Add to requirements.txt:**
```bash
# Add package
pip install new-package

# Update requirements
pip freeze > requirements.txt
```

2. **For Development Dependencies:**
```bash
# Add to requirements-dev.txt
echo "new-dev-package==1.0.0" >> requirements-dev.txt
```

### Dependency Updates

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements file
pip freeze > requirements.txt
```

## 🚀 Performance Considerations

### Database Optimization

1. **Use select_related and prefetch_related:**
```python
# Good
incidents = Incident.objects.select_related('reported_by', 'assigned_to')

# Bad
incidents = Incident.objects.all()
for incident in incidents:
    print(incident.reported_by.username)  # N+1 query problem
```

2. **Add Database Indexes:**
```python
class Incident(models.Model):
    status = models.CharField(max_length=20, db_index=True)
    priority = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
```

3. **Use Database Functions:**
```python
from django.db.models import Count, Q

# Aggregate queries
stats = Incident.objects.aggregate(
    total=Count('id'),
    open_count=Count('id', filter=Q(status='open'))
)
```

### View Optimization

1. **Use Pagination:**
```python
from django.core.paginator import Paginator

def incident_list(request):
    incidents = Incident.objects.all()
    paginator = Paginator(incidents, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'incidents/list.html', {'page': page})
```

2. **Cache Expensive Operations:**
```python
from django.core.cache import cache

def get_incident_stats():
    stats = cache.get('incident_stats')
    if stats is None:
        stats = calculate_stats()  # Expensive operation
        cache.set('incident_stats', stats, 300)  # Cache for 5 minutes
    return stats
```

## 🔒 Security Guidelines

### Input Validation

1. **Always use Django forms:**
```python
# Good
form = IncidentForm(request.POST)
if form.is_valid():
    incident = form.save()

# Bad
title = request.POST.get('title')  # No validation
incident = Incident.objects.create(title=title)
```

2. **Escape user input in templates:**
```html
<!-- Good -->
<p>{{ incident.description|escape }}</p>

<!-- Bad -->
<p>{{ incident.description|safe }}</p>
```

### Authentication & Authorization

1. **Use login_required decorator:**
```python
@login_required
def incident_detail(request, incident_id):
    # View logic
```

2. **Check permissions:**
```python
def update_incident(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    
    # Check if user can edit
    if incident.reported_by != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
```

## 📚 Resources

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

### Tools
- [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Import Sorter](https://pycqa.github.io/isort/)

### Testing
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

This development guide should help you get started with contributing to the Incident Management System. For questions or clarifications, please reach out to the development team. 