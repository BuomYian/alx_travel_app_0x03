"""
Celery configuration for alx_travel_app project.
This module sets up Celery with RabbitMQ as the message broker.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')

# Create Celery instance
app = Celery('alx_travel_app')

# Load configuration from Django settings with CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """
    Debug task for testing Celery setup.
    """
    print(f'Request: {self.request!r}')
