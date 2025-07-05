# tasks/urls.py
from django.urls import path
from .views import( TaskCreateView,TaskDetailView,
                   TaskDetailView, AcceptTaskView, 
                   CompleteTaskView, PayTaskView, 
                   TaskUpdateView, CancelTaskView, 
                   MyTasksListView,ApplyToTaskView,
                   AssignApplicantView,CancelApplicationView,
                   OwnerFeedbackUpdateView)

# El namespace para estas URLs.
app_name = 'tasks'

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    
    path('<int:pk>/accept/', AcceptTaskView.as_view(), name='accept_task'),
    path('<int:pk>/complete/', CompleteTaskView.as_view(), name='complete_task'),
    path('<int:pk>/pay/', PayTaskView.as_view(), name='pay_task'),
    path('<int:pk>/update/', TaskUpdateView.as_view(), name='update_task'),
    path('<int:pk>/cancel/', CancelTaskView.as_view(), name='cancel_task'),
    path('my_tasks/', MyTasksListView.as_view(), name='my_tasks'),
    path('tasks/<int:pk>/apply/', ApplyToTaskView.as_view(), name='apply_to_task'),
    path('tasks/<int:task_pk>/assign/<int:applicant_id>/', AssignApplicantView.as_view(), name='assign_applicant'),
    path('<int:task_id>/cancel-application/', CancelApplicationView.as_view(), name='cancel_application'),
    path('task/<int:pk>/owner-feedback/', OwnerFeedbackUpdateView.as_view(), name='owner_feedback'),
]

     
