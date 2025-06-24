# incidents/admin.py

from django.contrib import admin
from .models import Incident, IncidentComment, IncidentAttachment


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Incident model
    """
    list_display = [
        'id', 'title', 'category', 'priority', 'status', 
        'reported_by', 'assigned_to', 'created_at'
    ]
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description', 'reported_by__username']
    list_editable = ['status', 'priority', 'assigned_to']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Assignment', {
            'fields': ('reported_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'reported_by', 'assigned_to'
        )


@admin.register(IncidentComment)
class IncidentCommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for IncidentComment model
    """
    list_display = ['id', 'incident', 'author', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'incident__title', 'author__username']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'incident', 'author'
        )


@admin.register(IncidentAttachment)
class IncidentAttachmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for IncidentAttachment model
    """
    list_display = ['id', 'incident', 'filename', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['filename', 'incident__title']
    readonly_fields = ['uploaded_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'incident', 'uploaded_by'
        )