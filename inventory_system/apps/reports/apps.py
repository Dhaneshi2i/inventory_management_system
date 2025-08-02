"""
Reports app configuration.
"""
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    """Configuration for the reports app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_system.apps.reports'
    verbose_name = 'Reports'
