"""
Alerts app configuration.
"""
from django.apps import AppConfig


class AlertsConfig(AppConfig):
    """Configuration for the alerts app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_system.apps.alerts'
    verbose_name = 'Alerts'
