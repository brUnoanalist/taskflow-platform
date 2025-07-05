# tasks/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.views import View
from .models import Task ,Application
from .forms import TaskForm,OwnerFeedbackForm
from django.db.models import Avg

User = get_user_model()

class TaskListHomeView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'home.html'
    context_object_name = 'available_to_accept_tasks' # Rename the context object here

    def get_queryset(self):
        current_user = self.request.user
        # This queryset will ONLY fetch tasks that are POSTED and available for the current user to accept.
        return Task.objects.filter(
            status=Task.Status.POSTED,
            assigned_to__isnull=True
        ).exclude(
            posted_by=current_user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The 'available_to_accept_tasks' is now set by context_object_name

        # --- Global Statistics for Hero Section (KEEP THESE) ---
        total_tasks = Task.objects.count()

        if total_tasks > 0:
            context['posted_percentage'] = int((Task.objects.filter(status=Task.Status.POSTED).count() / total_tasks) * 100)
            context['in_progress_percentage'] = int((Task.objects.filter(status=Task.Status.IN_PROGRESS).count() / total_tasks) * 100)
            context['completed_percentage'] = int((Task.objects.filter(status=Task.Status.COMPLETED).count() / total_tasks) * 100)
            context['paid_percentage'] = int((Task.objects.filter(status=Task.Status.PAID).count() / total_tasks) * 100)
            context['cancelled_percentage'] = int((Task.objects.filter(status=Task.Status.CANCELLED).count() / total_tasks) * 100)
        else:
            context['posted_percentage'] = 0
            context['in_progress_percentage'] = 0
            context['completed_percentage'] = 0
            context['paid_percentage'] = 0
            context['cancelled_percentage'] = 0
        
        # Pass Task.Status constants (still useful for _task_card.html)
        context['STATUS_POSTED'] = Task.Status.POSTED
        context['STATUS_IN_PROGRESS'] = Task.Status.IN_PROGRESS
        context['STATUS_COMPLETED'] = Task.Status.COMPLETED
        context['STATUS_PAID'] = Task.Status.PAID
        context['STATUS_CANCELLED'] = Task.Status.CANCELLED

        return context

class MyTasksListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/my_tasks.html' # NEW TEMPLATE
    context_object_name = 'my_tasks_all' # All tasks relevant to the user

    def get_queryset(self):
        current_user = self.request.user
        return Task.objects.filter(
            Q(posted_by=current_user) | Q(assigned_to=current_user)
        ).order_by('-created_at').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        
        # Further filter for display in separate sections on 'my_tasks.html'
        all_my_tasks = self.get_queryset() # Use the queryset from this view

        context['tasks_posted_by_me'] = all_my_tasks.filter(
            posted_by=current_user
        ).order_by('-created_at')

        context['tasks_assigned_to_me'] = all_my_tasks.filter(
            assigned_to=current_user
        ).exclude( # Exclude completed/paid/cancelled from current assigned list
            status__in=[Task.Status.COMPLETED, Task.Status.PAID, Task.Status.CANCELLED]
        ).order_by('-created_at')

        context['tasks_completed_by_me'] = all_my_tasks.filter(
            assigned_to=current_user,
            status=Task.Status.COMPLETED
        ).order_by('-updated_at') # Order by updated for recent completion

        context['tasks_posted_and_completed'] = all_my_tasks.filter(
            posted_by=current_user,
            status=Task.Status.COMPLETED
        ).order_by('-updated_at')
        
        context['tasks_posted_and_paid'] = all_my_tasks.filter(
            posted_by=current_user,
            status=Task.Status.PAID
        ).order_by('-updated_at')

        # Pass status constants
        context['STATUS_POSTED'] = Task.Status.POSTED
        context['STATUS_IN_PROGRESS'] = Task.Status.IN_PROGRESS
        context['STATUS_COMPLETED'] = Task.Status.COMPLETED
        context['STATUS_PAID'] = Task.Status.PAID
        context['STATUS_CANCELLED'] = Task.Status.CANCELLED

        return context

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()

        context['applicant_ids'] = list(task.applications.values_list('applicant__id', flat=True))

        context['STATUS_POSTED'] = Task.Status.POSTED
        context['STATUS_IN_PROGRESS'] = Task.Status.IN_PROGRESS
        context['STATUS_COMPLETED'] = Task.Status.COMPLETED
        context['STATUS_PAID'] = Task.Status.PAID
        context['STATUS_CANCELLED'] = Task.Status.CANCELLED

        context['TERMINAL_STATUSES'] = [
            Task.Status.COMPLETED,
            Task.Status.PAID,
            Task.Status.CANCELLED,
        ]

        # Nueva lógica: permitir calificación del trabajador
        context['can_leave_review'] = (
            task.status in [Task.Status.COMPLETED, Task.Status.PAID] and
            self.request.user == task.posted_by and
            task.assigned_to is not None and
            task.owner_rating is None
        )

        return context


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    context_object_name = 'task'

    def get_success_url(self):
        messages.success(self.request, f'La tarea "{self.object.title}" ha sido actualizada con éxito.')
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        task = self.get_object()
        return (self.request.user == task.posted_by and
                task.status == Task.Status.POSTED) # Use Task.Status.POSTED

    # No need for get_form_kwargs or form_invalid unless you have specific logic there
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['request'] = self.request
    #     return kwargs

    # def form_valid(self, form):
    #     messages.success(self.request, f'La tarea "{form.instance.title}" ha sido actualizada con éxito.')
    #     return super().form_valid(form)

    # def form_invalid(self, form):
    #     messages.error(self.request, 'Hubo un error al actualizar la tarea. Por favor, revisa los datos.')
    #     return super().form_invalid(form)

class ApplyToTaskView(LoginRequiredMixin, View):
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        if task.status != Task.Status.POSTED or task.posted_by == request.user:
            messages.error(request, "No puedes postularte a esta tarea.")
            return redirect('tasks:task_detail', pk=pk)

        if Application.objects.filter(task=task, applicant=request.user).exists():
            messages.warning(request, "Ya te has postulado a esta tarea.")
            return redirect('tasks:task_detail', pk=pk)

        Application.objects.create(task=task, applicant=request.user)
        messages.success(request, "¡Postulación enviada!")
        return redirect('tasks:task_detail', pk=pk)

class AssignApplicantView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    def test_func(self):
        task = get_object_or_404(Task, pk=self.kwargs['task_pk'])
        return self.request.user == task.posted_by and task.status == Task.Status.POSTED

    def post(self, request, task_pk, applicant_id):
        task = get_object_or_404(Task, pk=task_pk)
        applicant = get_object_or_404(User, pk=applicant_id)

        task.assigned_to = applicant
        task.status = Task.Status.IN_PROGRESS
        task.save()

        messages.success(request, f'Has asignado la tarea a {applicant.email}.')
        return redirect('tasks:task_detail', pk=task_pk)
    
class AcceptTaskView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        # Corrected: Use Task.Status.POSTED here
        return (task.status == Task.Status.POSTED and
                self.request.user != task.posted_by and
                task.assigned_to is None)

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                task = Task.objects.select_for_update().get(pk=self.kwargs['pk'])

                # Re-check conditions after locking, using Task.Status.POSTED
                if (task.status == Task.Status.POSTED and
                    self.request.user != task.posted_by and
                    task.assigned_to is None):

                    task.status = Task.Status.IN_PROGRESS # Set to IN_PROGRESS
                    task.assigned_to = request.user
                    task.save()
                    messages.success(
                        request,
                        f'Has aceptado la tarea "{task.title}". ¡A trabajar!'
                    )
                    return redirect('tasks:task_detail', pk=task.pk)
                else:
                    messages.error(
                        request,
                        'No se pudo aceptar la tarea (estado inválido o ya asignada).'
                    )
                    return redirect('tasks:task_detail', pk=task.pk)
        except Task.DoesNotExist:
            messages.error(request, 'La tarea que intentas aceptar no existe.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error inesperado al procesar la solicitud: {e}')
            return redirect('tasks:task_detail', pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CompleteTaskView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        return (task.status == Task.Status.IN_PROGRESS and
                self.request.user == task.assigned_to)

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                task = Task.objects.select_for_update().get(pk=self.kwargs['pk'])

                if (task.status == Task.Status.IN_PROGRESS and
                    self.request.user == task.assigned_to):

                    task.status = Task.Status.COMPLETED
                    # task.completed_at = timezone.now() # Uncomment if you add this field to your model
                    task.save()

                    messages.success(
                        request,
                        f'¡Felicidades! La tarea "{task.title}" ha sido marcada como completada y está pendiente de revisión/pago.'
                    )
                    return redirect('tasks:task_detail', pk=task.pk)
                else:
                    messages.error(
                        request,
                        'No puedes completar esta tarea. Revisa su estado o si eres el asignado.'
                    )
                    return redirect('tasks:task_detail', pk=task.pk)
        except Task.DoesNotExist:
            messages.error(request, 'La tarea que intentas completar no existe.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado al completar la tarea: {e}')
            return redirect('tasks:task_detail', pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        messages.error(request, 'Acceso inválido. Por favor, usa el botón "Marcar como Completada".')
        return redirect('tasks:task_detail', pk=self.kwargs['pk'])


class PayTaskView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        return (task.status == Task.Status.COMPLETED and
                self.request.user == task.posted_by)

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                task = Task.objects.select_for_update().get(pk=self.kwargs['pk'])

                if (task.status == Task.Status.COMPLETED and
                    self.request.user == task.posted_by):

                    task.status = Task.Status.PAID
                    task.save()

                    messages.success(
                        request,
                        f'¡Tarea "{task.title}" marcada como pagada con éxito!'
                    )
                    return redirect('tasks:task_detail', pk=task.pk)
                else:
                    messages.error(
                        request,
                        'No puedes marcar esta tarea como pagada. Revisa su estado o si eres quien la publicó.'
                    )
                    return redirect('tasks:task_detail', pk=task.kwargs['pk']) # Typo here, should be self.kwargs['pk']
        except Task.DoesNotExist:
            messages.error(request, 'La tarea que intentas marcar como pagada no existe.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado al marcar la tarea como pagada: {e}')
            return redirect('tasks:task_detail', pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        messages.error(request, 'Acceso inválido. Por favor, usa el botón "Marcar como Pagada".')
        return redirect('tasks:task_detail', pk=self.kwargs['pk'])


class CancelTaskView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Vista para cancelar una tarea.
    - Cambia el estado de la tarea a 'CANCELLED'.
    - Solo el 'posted_by' puede cancelar la tarea.
    """
    model = Task
    template_name = 'tasks/task_detail.html' # Dummy template, we'll redirect
    context_object_name = 'task'

    def test_func(self):
        task = self.get_object()
        return (task.status in [Task.Status.POSTED, Task.Status.IN_PROGRESS] and
                self.request.user == task.posted_by)

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                task = Task.objects.select_for_update().get(pk=self.kwargs['pk'])

                if (task.status in [Task.Status.POSTED, Task.Status.IN_PROGRESS] and
                    self.request.user == task.posted_by):

                    task.status = Task.Status.CANCELLED

                    if task.assigned_to:
                        messages.info(
                            request,
                            f'¡Atención! La tarea "{task.title}" ha sido cancelada por quien la publicó.'
                        )
                        task.assigned_to = None
                    else:
                        messages.success(
                            request,
                            f'Tarea "{task.title}" cancelada con éxito.'
                        )
                    task.save()

                    return redirect('tasks:task_detail', pk=task.pk)
                else:
                    messages.error(
                        request,
                        'No puedes cancelar esta tarea. Revisa su estado o si eres quien la publicó.'
                    )
                    return redirect('tasks:task_detail', pk=task.pk)
        except Task.DoesNotExist:
            messages.error(request, 'La tarea que intentas cancelar no existe.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Ocurrió un error inesperado al cancelar la tarea: {e}')
            return redirect('tasks:task_detail', pk=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        messages.error(request, 'Acceso inválido. Por favor, usa el botón "Cancelar Tarea" para esta acción.')
        return redirect('tasks:task_detail', pk=self.kwargs['pk'])
    
    
class CancelApplicationView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id)
        application = Application.objects.filter(task=task, applicant=request.user).first()

        if application and task.assigned_to is None:
            application.delete()
            messages.success(request, "Has cancelado tu postulación.")
        else:
            messages.error(request, "No puedes cancelar esta postulación.")

        return redirect('tasks:task_detail', pk=task_id)    
    
class OwnerFeedbackUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = OwnerFeedbackForm
    template_name = 'tasks/owner_feedback_form.html'

    def test_func(self):
        task = self.get_object()
        # Solo el dueño puede dejar feedback, y solo si la tarea está COMPLETADA o PAID
        return (self.request.user == task.posted_by and
                task.status in [Task.Status.COMPLETED, Task.Status.PAID])

    def get_success_url(self):
        return reverse_lazy('tasks:task_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        # Actualizar reputación del usuario asignado
        self.update_user_reputation()
        messages.success(self.request, "Tu comentario y calificación se guardaron correctamente.")
        return response

    def update_user_reputation(self):
        assigned_user = self.object.assigned_to
        if assigned_user:
            avg_rating = Task.objects.filter(
                assigned_to=assigned_user,
                owner_rating__isnull=False,
                status=Task.Status.PAID
            ).aggregate(avg_rating=Avg('owner_rating'))['avg_rating']

            if avg_rating:
                assigned_user.reputation = avg_rating
                assigned_user.save()    