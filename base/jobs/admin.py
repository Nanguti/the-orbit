from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'industry', 'publication_date', 'created_at']
    list_filter = ['industry']
    search_fields = ['title', 'description']
