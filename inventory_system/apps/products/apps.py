"""
Products app configuration.
"""
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Configuration for the products app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_system.apps.products'
    verbose_name = 'Products'
