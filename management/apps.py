import os
from django.apps import AppConfig


class ManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'management'

    def ready(self):
        # Hide APScheduler models from admin (they clutter the panel)
        from django.contrib import admin
        from django_apscheduler.models import DjangoJob, DjangoJobExecution
        try:
            admin.site.unregister(DjangoJob)
            admin.site.unregister(DjangoJobExecution)
        except admin.sites.NotRegistered:
            pass

        # Prevent the scheduler from starting twice in development
        if os.environ.get('RUN_MAIN'):
            from . import scheduler
            scheduler.start()
