from django.urls import path
from . import views

app_name = 'incidents'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('incidents/', views.IncidentListView.as_view(), name='incident_list'),
    path('incidents/create/', views.create_incident, name='create_incident'),
    path('incidents/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('incidents/<int:incident_id>/update/', views.update_incident, name='update_incident'),
    path('api/stats/', views.incident_stats_api, name='incident_stats_api'),
]