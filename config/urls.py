"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/reports/', include('management.report_urls')),
    path('admin/', admin.site.urls),
    path('api/', include('management.api_urls')),
    path('', RedirectView.as_view(pattern_name='kiosk', permanent=False)),
    path('', include('management.urls')),
]
