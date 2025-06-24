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

## 🐛 Debugging

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