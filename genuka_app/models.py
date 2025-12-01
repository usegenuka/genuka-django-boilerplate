from django.db import models


class Company(models.Model):
    """
    Company model for storing Genuka company information
    """
    id = models.CharField(max_length=255, primary_key=True)  # Genuka company ID
    handle = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    logo_url = models.URLField(max_length=500, null=True, blank=True)
    authorization_code = models.CharField(max_length=500, null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['handle']),
        ]

    def __str__(self):
        return f"{self.name} ({self.id})"
