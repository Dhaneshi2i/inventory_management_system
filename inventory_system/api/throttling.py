"""
API rate limiting configuration.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class UserRateThrottle(UserRateThrottle):
    """Rate limiting for authenticated users."""
    rate = '100/hour'  # 100 requests per hour for authenticated users


class AnonRateThrottle(AnonRateThrottle):
    """Rate limiting for anonymous users."""
    rate = '20/hour'  # 20 requests per hour for anonymous users


class BurstRateThrottle(UserRateThrottle):
    """Burst rate limiting for authenticated users."""
    rate = '10/minute'  # 10 requests per minute for authenticated users


class SustainedRateThrottle(UserRateThrottle):
    """Sustained rate limiting for authenticated users."""
    rate = '1000/day'  # 1000 requests per day for authenticated users 