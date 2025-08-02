"""
Celery configuration for background tasks.
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')

app = Celery('inventory_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery configuration
app.conf.update(
    # Task routing
    task_routes={
        'inventory_system.tasks.*': {'queue': 'default'},
        'inventory_system.tasks.periodic.*': {'queue': 'periodic'},
        'inventory_system.tasks.reports.*': {'queue': 'reports'},
        'inventory_system.tasks.notifications.*': {'queue': 'notifications'},
    },
    
    # Task serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,  # Set to True for testing
    task_eager_propagates=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Result backend
    result_backend='redis://localhost:6379/1',
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'check-stock-levels': {
            'task': 'inventory_system.tasks.periodic.check_stock_levels',
            'schedule': 300.0,  # Every 5 minutes
        },
        'generate-daily-reports': {
            'task': 'inventory_system.tasks.periodic.generate_daily_reports',
            'schedule': 86400.0,  # Daily
        },
        'cleanup-old-data': {
            'task': 'inventory_system.tasks.periodic.cleanup_old_data',
            'schedule': 604800.0,  # Weekly
        },
        'send-alert-notifications': {
            'task': 'inventory_system.tasks.notifications.send_alert_notifications',
            'schedule': 600.0,  # Every 10 minutes
        },
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Retry configuration
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'


if __name__ == '__main__':
    app.start() 