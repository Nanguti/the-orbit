from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from jobs.views import JobViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('monitor/', include('monitor.urls')),
]
