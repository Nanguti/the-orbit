from django.urls import path
from . import views

app_name = 'monitor'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('task-status/', views.task_status, name='task-status'),
] 