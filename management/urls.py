from django.urls import path
from . import views

urlpatterns = [
    path('kiosk/', views.kiosk, name='kiosk'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('renew/', views.renew_request, name='renew_request'),
    path('issue-book/', views.issue_book_manual, name='issue_book_manual'),
    path('admin-manual-reminder/', views.admin_manual_reminder, name='admin_manual_reminder'),
    path('search/', views.book_search, name='book_search'),
]
