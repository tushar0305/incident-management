from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from incidents.models import Incident, Category, Priority, Status
import random
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create users if they don't exist
        users = []
        user_data = [
            ('admin', 'admin@example.com', 'Admin', 'User'),
            ('john_doe', 'john@example.com', 'John', 'Doe'),
            ('jane_smith', 'jane@example.com', 'Jane', 'Smith'),
            ('mike_wilson', 'mike@example.com', 'Mike', 'Wilson'),
            ('sarah_brown', 'sarah@example.com', 'Sarah', 'Brown'),
        ]

        for username, email, first_name, last_name in user_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': True if username == 'admin' else False,
                    'is_superuser': True if username == 'admin' else False,
                }
            )
            if created:
                user.set_password('password123')  # Set a default password
                user.save()
                self.stdout.write(f"Created user: {username}")
            else:
                self.stdout.write(f"User already exists: {username}")
            users.append(user)

        # Create categories
        categories_data = [
            ('Hardware', 'Hardware-related issues and failures'),
            ('Software', 'Software bugs and application issues'),
            ('Network', 'Network connectivity and infrastructure problems'),
            ('Security', 'Security incidents and breaches'),
            ('Database', 'Database performance and connectivity issues'),
            ('User Access', 'Account access and permission issues'),
        ]

        categories = []
        for name, description in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f"Created category: {name}")
            categories.append(category)

        # Sample incident data
        incident_templates = [
            {
                'title': 'Server CPU Usage High',
                'description': 'Production server showing consistently high CPU usage above 90%. Performance degradation observed.',
                'priority': Priority.HIGH,
                'category': 'Hardware'
            },
            {
                'title': 'Login Page Not Loading',
                'description': 'Users reporting that the login page is not loading properly. Getting 500 error intermittently.',
                'priority': Priority.CRITICAL,
                'category': 'Software'
            },
            {
                'title': 'WiFi Connection Drops',
                'description': 'Office WiFi connection dropping frequently in the east wing. Multiple users affected.',
                'priority': Priority.MEDIUM,
                'category': 'Network'
            },
            {
                'title': 'Suspicious Login Attempts',
                'description': 'Multiple failed login attempts detected from unusual IP addresses. Possible brute force attack.',
                'priority': Priority.HIGH,
                'category': 'Security'
            },
            {
                'title': 'Database Query Timeout',
                'description': 'Customer database queries timing out during peak hours. Response time exceeded 30 seconds.',
                'priority': Priority.HIGH,
                'category': 'Database'
            },
            {
                'title': 'User Cannot Access CRM',
                'description': 'New employee unable to access CRM system. Permissions may not be configured correctly.',
                'priority': Priority.LOW,
                'category': 'User Access'
            },
            {
                'title': 'Email Server Down',
                'description': 'Corporate email server is unresponsive. No emails being sent or received.',
                'priority': Priority.CRITICAL,
                'category': 'Network'
            },
            {
                'title': 'Application Memory Leak',
                'description': 'Customer portal application consuming excessive memory. System restart required every few hours.',
                'priority': Priority.MEDIUM,
                'category': 'Software'
            },
            {
                'title': 'Backup System Failure',
                'description': 'Nightly backup process failed for the third consecutive day. Data integrity at risk.',
                'priority': Priority.HIGH,
                'category': 'Hardware'
            },
            {
                'title': 'SSL Certificate Expired',
                'description': 'SSL certificate for main website has expired. Users seeing security warnings.',
                'priority': Priority.CRITICAL,
                'category': 'Security'
            },
        ]

        # Create incidents
        incidents_created = 0
        for i, template in enumerate(incident_templates):
            # Find the category object
            category = next((cat for cat in categories if cat.name == template['category']), None)
            
            # Random dates for variety
            days_ago = random.randint(1, 30)
            created_date = timezone.now() - timedelta(days=days_ago)
            
            # Random status (weighted towards open/in_progress for active incidents)
            status_choices = [Status.OPEN, Status.IN_PROGRESS, Status.RESOLVED, Status.CLOSED]
            status_weights = [0.3, 0.4, 0.2, 0.1]  # More open/in_progress incidents
            status = random.choices(status_choices, weights=status_weights)[0]
            
            # Set resolved_at if status is resolved or closed
            resolved_at = None
            if status in [Status.RESOLVED, Status.CLOSED]:
                resolved_at = created_date + timedelta(
                    hours=random.randint(1, 72)  # Resolved within 1-72 hours
                )

            incident = Incident.objects.create(
                title=template['title'],
                description=template['description'],
                priority=template['priority'],
                status=status,
                category=category,
                reporter=random.choice(users),
                assigned_to=random.choice(users) if random.random() > 0.2 else None,  # 80% chance of assignment
                created_at=created_date,
                resolved_at=resolved_at,
            )
            incidents_created += 1

        # Create some additional random incidents for volume
        additional_titles = [
            'Printer Offline in Conference Room',
            'VPN Connection Issues',
            'File Share Access Denied',
            'Website Loading Slowly',
            'Mobile App Crashes on Startup',
            'Payment Gateway Error',
            'Report Generation Failing',
            'User Account Locked',
            'Disk Space Running Low',
            'API Rate Limit Exceeded',
        ]

        for title in additional_titles:
            days_ago = random.randint(1, 60)
            created_date = timezone.now() - timedelta(days=days_ago)
            
            status = random.choices(
                [Status.OPEN, Status.IN_PROGRESS, Status.RESOLVED, Status.CLOSED],
                weights=[0.25, 0.35, 0.25, 0.15]
            )[0]
            
            resolved_at = None
            if status in [Status.RESOLVED, Status.CLOSED]:
                resolved_at = created_date + timedelta(
                    hours=random.randint(1, 120)
                )

            Incident.objects.create(
                title=title,
                description=f"Description for {title}. This is a sample incident created for testing purposes.",
                priority=random.choice([Priority.LOW, Priority.MEDIUM, Priority.HIGH, Priority.CRITICAL]),
                status=status,
                category=random.choice(categories),
                reporter=random.choice(users),
                assigned_to=random.choice(users) if random.random() > 0.3 else None,
                created_at=created_date,
                resolved_at=resolved_at,
            )
            incidents_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(users)} users\n'
                f'- {len(categories)} categories\n'
                f'- {incidents_created} incidents'
            )
        )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating sample data',
        )

        if self.options.get('clear'):
            self.stdout.write('Clearing existing data...')
            Incident.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write('Existing data cleared.')