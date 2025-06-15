# tasks/views.py
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView 
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task
from .forms import TaskForm
    

class TaskListHomeView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'home.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        """
        Este método ahora filtra las tareas para dos condiciones:
        1. Solo muestra tareas con el estado 'POSTED'.
        2. Excluye las tareas donde el 'posted_by' es el usuario actual.
        """
        # Obtenemos el usuario que está haciendo la petición.
        current_user = self.request.user
        
        # Construimos el queryset.
        return Task.objects.filter(
            status='POSTED'
        ).exclude(
            posted_by=current_user
        ).order_by('-created_at')
    
class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear una nueva tarea.
    - LoginRequiredMixin: Protege la vista, solo usuarios autenticados pueden acceder.
    - CreateView: Maneja la lógica de mostrar un formulario y guardar un nuevo objeto.
    """
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    # Redirige a la página 'home' si la creación es exitosa.
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """
        Este método se llama cuando los datos del formulario son válidos.
        Aquí asignamos el usuario actual como el creador de la tarea
        antes de guardarla en la base de datos.
        """
        form.instance.posted_by = self.request.user
        return super().form_valid(form)    