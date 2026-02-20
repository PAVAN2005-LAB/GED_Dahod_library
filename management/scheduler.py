import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from .tasks import send_due_reminders

logger = logging.getLogger('management')


def start():
    """Initialize the APScheduler with background tasks."""
    scheduler = BackgroundScheduler(timezone='Asia/Kolkata')
    scheduler.add_jobstore(DjangoJobStore(), "default")



    # Task B: Daily at 8 AM — send due book reminders
    scheduler.add_job(
        send_due_reminders,
        trigger="cron",
        hour=8,
        minute=0,
        id="send_due_reminders",
        max_instances=1,
        replace_existing=True,
    )

    register_events(scheduler)
    scheduler.start()
    logger.info("APScheduler started with 1 scheduled task.")
