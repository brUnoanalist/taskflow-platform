# tasks/forms.py
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """
    Formulario para la creación y edición de Tareas.
    Al heredar de ModelForm, Django se encarga de la validación
    y la creación de campos basados en el modelo Task.
    """
    class Meta:
        model = Task
        # Especificamos explícitamente los campos que el usuario puede rellenar.
        # Campos como 'posted_by' y 'status' se asignan en la vista
        # para garantizar la integridad y seguridad de los datos.
        fields = ['title', 'description', 'reward']