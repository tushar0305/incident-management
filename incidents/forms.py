from django import forms
from django.contrib.auth.models import User
from .models import Incident, IncidentComment, IncidentAttachment


class IncidentForm(forms.ModelForm):
    """
    Form for creating and updating incidents
    """
    
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'priority', 'status', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter incident title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the incident in detail'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate assigned_to with all users
        self.fields['assigned_to'].queryset = User.objects.all()
        self.fields['assigned_to'].empty_label = "-- Select assignee --"
        
        # Make fields required
        self.fields['title'].required = True
        self.fields['description'].required = True


class IncidentCommentForm(forms.ModelForm):
    """
    Form for adding comments to incidents
    """
    
    class Meta:
        model = IncidentComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment or update...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = True


class IncidentSearchForm(forms.Form):
    """
    Form for searching and filtering incidents
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search incidents...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Incident.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + Incident.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + Incident.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned = forms.ChoiceField(
        choices=[('', 'All Assignments'), ('me', 'My Incidents')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class IncidentAttachmentForm(forms.ModelForm):
    """
    Form for uploading attachments to incidents
    """
    class Meta:
        model = IncidentAttachment
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True