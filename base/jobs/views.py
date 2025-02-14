from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters import rest_framework as django_filters
from .models import Job
from .serializers import JobSerializer
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class JobFilter(django_filters.FilterSet):
    skills = django_filters.CharFilter(method='filter_skills')
    industry = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Job
        fields = ['industry', 'skills']

    def filter_skills(self, queryset, name, value):
        skills = [s.strip() for s in value.split(',')]
        return queryset.filter(skills__overlap=skills)

class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [AllowAny]
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = JobFilter
    ordering_fields = ['publication_date']
    ordering = ['-publication_date']

    def list(self, request, *args, **kwargs):
        logger.info(f"Total jobs in database: {Job.objects.count()}")
        return super().list(request, *args, **kwargs)
