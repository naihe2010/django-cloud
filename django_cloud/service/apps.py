import os
from django.apps import AppConfig
from django.utils.autoreload import DJANGO_AUTORELOAD_ENV
from . import service


class ServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cloud.service'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self.service_manager = service.ServiceManager()

    def ready(self):
        if os.environ.get(DJANGO_AUTORELOAD_ENV):
            self.service_manager.start()
