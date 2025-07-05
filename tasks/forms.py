# tasks/forms.py
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'reward', 'due_date'] # Exclude 'posted_by', 'assigned_to', 'status', 'created_at', 'updated_at', 'completed_at'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'rows': 4}),
            'reward': forms.NumberInput(attrs={'class': 'form-input block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        }
        labels = {
            'title': 'Título de la Tarea',
            'description': 'Descripción Detallada',
            'reward': 'Recompensa ($)',
            'due_date': 'Fecha Límite (Opcional)',
        }
        
class OwnerFeedbackForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['owner_comment', 'owner_rating']
        widgets = {
            'owner_comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Deja un comentario sobre el trabajo...'}),
            'owner_rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 0.1}),
        }
        labels = {
            'owner_comment': 'Comentario',
            'owner_rating': 'Calificación (1.0 - 5.0)',
        }        