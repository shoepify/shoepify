from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoesite.settings')

app = Celery('shoesite')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# scheduled popularity update (NOT USED CURRENTLY)
''' 
app.conf.beat_schedule = {
    'update-popularity-scores': {
        'task': 'shoesite.tasks.update_all_popularity_scores',
        'schedule': crontab(hour=0, minute=0),  # Adjust to run at midnight every day
    },
}
'''