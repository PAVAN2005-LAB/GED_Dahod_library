from django.urls import path
from . import report_views

urlpatterns = [
    path('', report_views.reports_dashboard, name='reports_dashboard'),
    path('entry-exit/', report_views.download_entry_exit, name='report_entry_exit'),
    path('book-issues/', report_views.download_book_issues, name='report_book_issues'),
    path('overdue-students/', report_views.download_overdue_students, name='report_overdue_students'),
]
