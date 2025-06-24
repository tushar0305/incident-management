from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Incident(models.Model):
    """
    Main incident model to track issues and problems
    """

    id = models.AutoField(primary_key=True)
    
    # Incident priority levels
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Incident status options
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    # Incident categories
    CATEGORY_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('network', 'Network'),
        ('security', 'Security'),
        ('other', 'Other'),
    ]
    
    # Basic incident information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # User assignments
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"#{self.id} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Auto-set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'resolved':
            self.resolved_at = None
            
        super().save(*args, **kwargs)


class IncidentComment(models.Model):
    """
    Comments/updates on incidents for tracking progress
    """
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Comment on {self.incident.title} by {self.author.username}"


class IncidentAttachment(models.Model):
    """
    File attachments for incidents (screenshots, logs, etc.)
    """
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='incident_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Attachment for {self.incident.title}: {self.filename}"