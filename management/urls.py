from django.urls import path
from . import views

urlpatterns = [
    path('kiosk/', views.kiosk, name='kiosk'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
