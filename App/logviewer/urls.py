# logviewer/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.log_view, name='log_view'),
    path('scan/csrf/', views.csrf_scan_view, name='csrf_scan'),
    path('scan/sql_injection/', views.sql_scan_view, name='sql_injection_scan'),
    path('scan/xss/', views.xss_scan_view, name='xss_scan'),
    path('scan/cors/', views.cors_scan_view, name='cors_scan'),
]
