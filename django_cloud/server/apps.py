from django.apps import AppConfig
from django.utils.autoreload import DJANGO_AUTORELOAD_ENV


class ServerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cloud.server'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        from .server import Server
        self.__server = Server()

    def ready(self):
        import os
        if os.environ.get(DJANGO_AUTORELOAD_ENV):
            self.__server.start()
