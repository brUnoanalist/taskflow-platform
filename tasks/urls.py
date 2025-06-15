# tasks/urls.py
from django.urls import path
from .views import TaskCreateView

# El namespace para estas URLs.
app_name = 'tasks'

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='create'),
]