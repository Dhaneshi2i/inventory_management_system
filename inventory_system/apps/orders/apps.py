"""
Orders app configuration.
"""
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the orders app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_system.apps.orders'
    verbose_name = 'Orders'
