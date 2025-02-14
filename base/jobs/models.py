from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import URLValidator
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

# Create your models here.

class Job(models.Model):
    title = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    position = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    skills = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    tech_skills = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    soft_skills = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    job_link = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        unique=True
    )
    publication_date = models.DateTimeField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['industry']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['position']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company or 'Unknown Company'} ({self.location or 'Unknown Location'})"

    def save(self, *args, **kwargs):
        logger.info(f"Saving job: {self.title}")
        super().save(*args, **kwargs)

class JobAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    industries = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    skills = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    job_titles = ArrayField(
        models.CharField(max_length=255),
        blank=True,
        default=list
    )
    locations = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_sent']),
        ]

    def __str__(self):
        return f"Job Alert for {self.email}"
