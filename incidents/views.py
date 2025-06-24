from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Incident, IncidentComment
from .forms import IncidentForm, IncidentCommentForm, IncidentAttachmentForm
from .kafka_producer import send_incident_notification, send_status_update_notification


# Dashboard View
@login_required
def dashboard(request):
    incidents = Incident.objects.order_by('-created_at')[:5]
    stats = {
        'total': Incident.objects.count(),
        'open': Incident.objects.filter(status='open').count(),
        'resolved': Incident.objects.filter(status='resolved').count(),
        'high_priority': Incident.objects.filter(priority='high').count(),
    }
    return render(request, 'incidents/dashboard.html', {
        'incidents': incidents,
        'stats': stats
    })


# Incident List View
class IncidentListView(LoginRequiredMixin, ListView):
    """
    Display list of all incidents with filtering and pagination
    """
    model = Incident
    template_name = 'incidents/incident_list.html'
    context_object_name = 'incidents'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Incident.objects.all()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        # Filter by assigned user
        assigned = self.request.GET.get('assigned')
        if assigned == 'me':
            queryset = queryset.filter(assigned_to=self.request.user)
            
        return queryset


# Incident Detail View
@login_required
def incident_detail(request, incident_id):
    """
    Show detailed view of a single incident with comments and attachments
    """
    incident = get_object_or_404(Incident, id=incident_id)
    comments = incident.comments.all()
    attachments = incident.attachments.all()

    # Handle comment form submission
    comment_form = IncidentCommentForm()
    attachment_form = None
    can_upload = request.user == incident.reported_by or request.user == incident.assigned_to
    if can_upload:
        attachment_form = IncidentAttachmentForm()

    if request.method == 'POST':
        if 'add_comment' in request.POST:
            comment_form = IncidentCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.incident = incident
                comment.author = request.user
                comment.save()
                messages.success(request, 'Comment added successfully!')
                return redirect('incidents:incident_detail', incident_id=incident.id)
        elif 'add_attachment' in request.POST and can_upload:
            attachment_form = IncidentAttachmentForm(request.POST, request.FILES)
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.incident = incident
                attachment.uploaded_by = request.user
                attachment.filename = attachment.file.name
                attachment.save()
                messages.success(request, 'Attachment uploaded successfully!')
                return redirect('incidents:incident_detail', incident_id=incident.id)

    context = {
        'incident': incident,
        'comments': comments,
        'comment_form': comment_form,
        'attachments': attachments,
        'attachment_form': attachment_form,
        'can_upload': can_upload,
    }
    return render(request, 'incidents/incident_detail.html', context)


# Create New Incident
@login_required
def create_incident(request):
    """
    Create a new incident report
    """
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user
            incident.save()
            
            # Send notification via Kafka
            try:
                send_incident_notification(incident)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to send Kafka notification: {e}")
            
            messages.success(request, 'Incident created successfully!')
            return redirect('incidents:incident_detail', incident_id=incident.id)
    else:
        form = IncidentForm()
    
    return render(request, 'incidents/create_incident.html', {'form': form})


# Update Incident
@login_required
def update_incident(request, incident_id):
    """
    Update an existing incident
    """
    incident = get_object_or_404(Incident, id=incident_id)
    
    # Check if user can edit (owner or assigned user)
    if incident.reported_by != request.user and incident.assigned_to != request.user:
        messages.error(request, 'You do not have permission to edit this incident.')
        return redirect('incidents:incident_detail', incident_id=incident.id)
    
    if request.method == 'POST':
        # Store old status before updating
        old_status = incident.status
        
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            updated_incident = form.save()
            
            # Check if status changed and send Kafka notification
            if old_status != updated_incident.status:
                try:
                    send_status_update_notification(updated_incident, old_status, updated_incident.status)
                except Exception as e:
                    # Log error but don't fail the request
                    print(f"Failed to send status update notification: {e}")
            
            messages.success(request, 'Incident updated successfully!')
            return redirect('incidents:incident_detail', incident_id=incident.id)
    else:
        form = IncidentForm(instance=incident)
    
    context = {
        'form': form,
        'incident': incident,
    }
    return render(request, 'incidents/update_incident.html', context)


# API endpoint for incident statistics (for dashboard charts)
@login_required
def incident_stats_api(request):
    """
    API endpoint to get incident statistics for charts
    """
    stats = {
        'by_status': {
            'open': Incident.objects.filter(status='open').count(),
            'in_progress': Incident.objects.filter(status='in_progress').count(),
            'resolved': Incident.objects.filter(status='resolved').count(),
            'closed': Incident.objects.filter(status='closed').count(),
        },
        'by_priority': {
            'low': Incident.objects.filter(priority='low').count(),
            'medium': Incident.objects.filter(priority='medium').count(),
            'high': Incident.objects.filter(priority='high').count(),
            'critical': Incident.objects.filter(priority='critical').count(),
        },
        'by_category': {}
    }
    
    # Get category stats
    for category, _ in Incident.CATEGORY_CHOICES:
        stats['by_category'][category] = Incident.objects.filter(category=category).count()
    
    return JsonResponse(stats)

