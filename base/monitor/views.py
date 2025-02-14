from django.shortcuts import render
from django.utils import timezone
from jobs.models import Job
from datetime import timedelta
from django.db.models import Count
from django_celery_beat.models import PeriodicTask
from celery.app.control import Inspect
from base.celery import app
import json
from django.http import JsonResponse

def dashboard(request):
    # Get job statistics
    total_jobs = Job.objects.count()
    last_24h_jobs = Job.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Get jobs by industry
    jobs_by_industry = Job.objects.values('industry').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get Celery task information
    try:
        i = Inspect(app=app)
        active_tasks = i.active() or {}
        scheduled_tasks = i.scheduled() or {}
    except Exception as e:
        active_tasks = {'error': str(e)}
        scheduled_tasks = {'error': str(e)}
    
    # Get scheduled tasks from database
    periodic_tasks = PeriodicTask.objects.filter(enabled=True).select_related('interval', 'crontab')
    
    context = {
        'total_jobs': total_jobs,
        'last_24h_jobs': last_24h_jobs,
        'jobs_by_industry': jobs_by_industry,
        'active_tasks': json.dumps(active_tasks, indent=2),
        'scheduled_tasks': json.dumps(scheduled_tasks, indent=2),
        'periodic_tasks': periodic_tasks,
        'last_update': timezone.now(),
    }
    
    return render(request, 'monitor/dashboard.html', context)

def task_status(request):
    try:
        # Get the periodic task
        task = PeriodicTask.objects.get(name='fetch-jobs-every-5-minutes')
        
        # Get active tasks
        i = app.control.inspect()
        active = i.active() or {}
        scheduled = i.scheduled() or {}
        reserved = i.reserved() or {}
        
        # Get task statistics
        stats = {
            'total_jobs': Job.objects.count(),
            'recent_jobs': Job.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).count()
        }
        
        return JsonResponse({
            'status': 'success',
            'task_info': {
                'name': task.name,
                'last_run': task.last_run_at,
                'description': task.description,
                'enabled': task.enabled,
                'total_run_count': task.total_run_count,
            },
            'celery_info': {
                'active_tasks': active,
                'scheduled_tasks': scheduled,
                'reserved_tasks': reserved,
            },
            'stats': stats,
            'last_check': timezone.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'last_check': timezone.now().isoformat(),
        }, status=500) 