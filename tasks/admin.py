from django.contrib import admin
from .models import Task, Application

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'assigned_to', 'status', 'reward', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'posted_by__username')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('task', 'applicant', 'created_at')
    search_fields = ('task__title', 'applicant__username')
