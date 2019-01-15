from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magine_gui_app.settings')
app = Celery('magine_gui_app')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.control.broadcast(
    'rate_limit',
    arguments={'task_name': 'gui.enrichment_functions.tasks.run_set_of_dbs',
               'rate_limit': '1/m'}
)
