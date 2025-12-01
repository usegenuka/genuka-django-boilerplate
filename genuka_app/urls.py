"""
URL configuration for Genuka app
"""
from django.urls import path
from .views import (
    CallbackView,
    WebhookView,
    HealthView,
    CheckView,
    RefreshView,
    MeView,
    LogoutView,
)

urlpatterns = [
    # OAuth callback
    path('auth/callback', CallbackView.as_view(), name='auth_callback'),

    # Session management
    path('auth/check', CheckView.as_view(), name='auth_check'),
    path('auth/refresh', RefreshView.as_view(), name='auth_refresh'),
    path('auth/me', MeView.as_view(), name='auth_me'),
    path('auth/logout', LogoutView.as_view(), name='auth_logout'),

    # Webhook
    path('auth/webhook', WebhookView.as_view(), name='auth_webhook'),
]
