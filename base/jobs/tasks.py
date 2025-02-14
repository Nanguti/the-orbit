from celery import shared_task
from .services import JobFetcher
from .models import Job, JobAlert
from django.db import transaction
import logging
import time
from datetime import datetime, timezone, timedelta
from django_celery_beat.models import PeriodicTask
from .services import JobEmailService
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from typing import List, Tuple

logger = logging.getLogger(__name__)

@shared_task
def fetch_and_save_jobs():
    logger.info("\n=== Starting job fetch task ===")
    current_time = datetime.now()
    logger.info(f"Current time: {current_time}")
    
    try:
        # Get the periodic task and update its description with last run info
        task = PeriodicTask.objects.get(name='fetch-jobs-every-5-minutes')
        task.description = f"Last successful run: {current_time}"
        task.save()
        
        job_fetcher = JobFetcher()
        jobs = job_fetcher.fetch_jobs()
        
        logger.info(f"Found {len(jobs)} jobs to process")
        
        if not jobs:
            logger.warning("No jobs found to process")
            return "No jobs found to process"
        
        new_jobs = 0
        updated_jobs = 0

        with transaction.atomic():
            for job_data in jobs:
                job_link = job_data.get('job_link')
                if not job_link:
                    logger.warning(f"Missing job_link in data: {job_data}")
                    continue
                    
                logger.info(f"Processing job: {job_data}")  # Log entire job data
                
                try:
                    job, created = Job.objects.update_or_create(
                        job_link=job_link,
                        defaults={
                            'title': job_data['title'],
                            'industry': job_data['industry'],
                            'position': job_data['position'],
                            'company': job_data['company'],
                            'location': job_data['location'],
                            'skills': job_data['skills'],
                            'tech_skills': job_data['tech_skills'],
                            'soft_skills': job_data['soft_skills'],
                            'publication_date': job_data['publication_date'],
                            'description': job_data['description']
                        }
                    )
                    
                    if created:
                        new_jobs += 1
                        logger.info(f"Created new job: {job.title}")
                    else:
                        updated_jobs += 1
                        logger.info(f"Updated existing job: {job.title}")
                except Exception as e:
                    logger.error(f"Error saving job {job_data.get('title', 'Unknown')}: {str(e)}")
                    logger.exception("Full traceback:")
                    continue

        result = f"Job update complete. New jobs: {new_jobs}, Updated jobs: {updated_jobs}"
        logger.info(result)
        return result
    
    except Exception as e:
        logger.error(f"Error in fetch_and_save_jobs: {str(e)}")
        logger.exception("Full traceback:")
        raise

@shared_task
def test_task():
    try:
        logger.info("Test task is starting!")
        # Add some actual work to verify task execution
        time.sleep(2)  # Sleep for 2 seconds
        logger.info("Test task completed successfully!")
        return "Test task completed!"
    except Exception as e:
        logger.error(f"Test task failed with error: {str(e)}")
        raise

@shared_task
def test_celery():
    logger.info("Test task running")
    return "Test task complete"

@shared_task
def send_job_alerts():
    """
    Task to send job alert emails for new matching jobs
    """
    logger.info("Starting job alerts task")
    
    # Get active alerts
    alerts = JobAlert.objects.filter(is_active=True)
    
    for alert in alerts:
        try:
            # Get jobs since last alert
            query = Job.objects.all()
            
            if alert.last_sent:
                query = query.filter(created_at__gt=alert.last_sent)
            else:
                # If never sent, get last 24 hours
                query = query.filter(
                    created_at__gt=timezone.now() - timedelta(days=1)
                )
            
            # Apply filters
            if alert.industries:
                query = query.filter(industry__in=alert.industries)
            if alert.skills:
                query = query.filter(tech_skills__overlap=alert.skills)
            if alert.job_titles:
                query = query.filter(title__in=alert.job_titles)
            if alert.locations:
                query = query.filter(location__in=alert.locations)
            
            matching_jobs = query.order_by('-created_at')
            
            if matching_jobs.exists():
                # Send email
                alert_criteria = {
                    'industries': alert.industries,
                    'skills': alert.skills,
                    'job_titles': alert.job_titles,
                    'locations': alert.locations
                }
                
                success = JobEmailService.send_job_alert(
                    alert.email,
                    matching_jobs,
                    alert_criteria
                )
                
                if success:
                    # Update last_sent timestamp
                    alert.last_sent = timezone.now()
                    alert.save()
                    logger.info(f"Sent job alert to {alert.email}")
                
        except Exception as e:
            logger.error(f"Error processing alert for {alert.email}: {str(e)}")
            continue
    
    logger.info("Completed job alerts task")

class JobEmailService:
    @staticmethod
    def batch_send_alerts(alerts: List[Tuple[str, List[Job], dict]]) -> None:
        """Send email alerts in batch"""
        connection = get_connection()
        messages = []
        
        for email, jobs, criteria in alerts:
            context = {
                'jobs': jobs,
                'criteria': criteria
            }
            
            html_content = render_to_string('jobs/email/job_alert.html', context)
            text_content = render_to_string('jobs/email/job_alert.txt', context)
            
            message = EmailMultiAlternatives(
                subject='New Job Matches Found!',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                connection=connection
            )
            message.attach_alternative(html_content, "text/html")
            messages.append(message)
        
        # Send all emails in one connection
        connection.send_messages(messages) 