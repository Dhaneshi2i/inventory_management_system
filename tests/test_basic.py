"""
Basic tests to verify the testing setup works.
"""
import pytest
from django.test import TestCase


@pytest.mark.django_db
class TestBasicSetup:
    """Test basic setup."""
    
    def test_django_setup(self):
        """Test that Django is properly configured."""
        from django.conf import settings
        assert settings.DEBUG is not None
        assert 'inventory_system.apps.products' in settings.INSTALLED_APPS
    
    def test_database_connection(self):
        """Test database connection."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1


class TestBasicModels:
    """Test basic model functionality."""
    
    @pytest.mark.django_db
    def test_category_creation(self):
        """Test basic category creation."""
        from inventory_system.apps.products.models import Category
        
        category = Category.objects.create(
            name='Test Category',
            description='A test category'
        )
        
        assert category.name == 'Test Category'
        assert category.description == 'A test category'
        assert not category.is_deleted
    
    @pytest.mark.django_db
    def test_product_creation(self):
        """Test basic product creation."""
        from inventory_system.apps.products.models import Category, Product
        from decimal import Decimal
        
        category = Category.objects.create(
            name='Test Category',
            description='A test category'
        )
        
        product = Product.objects.create(
            name='Test Product',
            sku='TEST001',
            category=category,
            description='A test product',
            unit_price=Decimal('99.99')
        )
        
        assert product.name == 'Test Product'
        assert product.sku == 'TEST001'
        assert product.category == category
        assert product.unit_price == Decimal('99.99') 