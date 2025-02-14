# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use app password for Gmail
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Add to CELERY_BEAT_SCHEDULE
CELERY_BEAT_SCHEDULE = {
    # ... existing tasks ...
    'send-job-alerts': {
        'task': 'jobs.tasks.send_job_alerts',
        'schedule': 3600.0,  # Run hourly
    },
} 