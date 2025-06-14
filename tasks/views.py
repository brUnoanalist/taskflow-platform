# tasks/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView # Asegúrate de que ListView esté aquí
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task
#from .forms import TaskForm

class TaskListHomeView(LoginRequiredMixin, ListView): # Añade LoginRequiredMixin
    model = Task
    template_name = 'app_base.html' # Esto es correcto, ya que home.html hereda de app_base
    context_object_name = 'tasks'
    # ... el resto de la vista se queda igual ...

class TaskListHomeView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'home.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(status='POSTED').order_by('-created_at')
    