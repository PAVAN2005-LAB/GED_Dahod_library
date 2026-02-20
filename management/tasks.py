import logging
from datetime import timedelta
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import LibraryLog, Transaction

logger = logging.getLogger('management')




def send_due_reminders():
    """Task B: Send email reminders for books issued exactly 14 days ago (due today)."""
    today = timezone.now().date()
    fourteen_days_ago = today - timedelta(days=14)

    overdue_transactions = Transaction.objects.filter(
        issue_date__date=fourteen_days_ago,
        returned=False,
    ).select_related('student', 'book')

    sent_count = 0
    failed_count = 0

    for tx in overdue_transactions:
        # Build template context
        context = {
            'student_name': tx.student.name,
            'enrollment_id': tx.student.enrollment_id,
            'book_title': tx.book.title,
            'access_code': tx.book.access_code,
            'shelf_location': tx.book.shelf_location,
            'issue_date': tx.issue_date.strftime('%d %b, %Y'),
            'due_date': tx.due_date.strftime('%d %b, %Y'),
        }

        subject = f"📚 Library Reminder: Return '{tx.book.title}'"
        text_body = render_to_string('management/email/reminder.txt', context)
        html_body = render_to_string('management/email/reminder.html', context)

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[tx.student.email],
            )
            email.attach_alternative(html_body, 'text/html')
            email.send(fail_silently=False)

            sent_count += 1
            logger.info("Sent due reminder to %s for book '%s'.", tx.student.email, tx.book.title)
        except Exception:
            failed_count += 1
            logger.exception("Failed to send email to %s for book '%s'.", tx.student.email, tx.book.title)

    logger.info("Due reminders complete: %d sent, %d failed.", sent_count, failed_count)
