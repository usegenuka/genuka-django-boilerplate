"""
URL configuration for Genuka app
"""
from django.urls import path
from .views import CallbackView, WebhookView, HealthView

urlpatterns = [
    path('auth/callback', CallbackView.as_view(), name='auth_callback'),
    path('auth/webhook', WebhookView.as_view(), name='auth_webhook'),
]
