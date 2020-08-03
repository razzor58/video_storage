import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'video_storage.settings')
app = Celery('video_storage',
             broker=os.environ.get('CELERY_BROKER'),
             backend=os.environ.get('CELERY_BROKER'))

app.autodiscover_tasks()
