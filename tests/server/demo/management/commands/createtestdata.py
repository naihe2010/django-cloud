from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django_cloud.server.models import Service


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Refreshing test service data...")
        Service.objects.all().delete()
        Service.objects.create(name='service1',key='demo1', url='http://127.0.0.1:8001/service/').save()
        Service.objects.create(name='service1',key='demo2', url='http://127.0.0.1:8001/service2/').save()
        print("Refreshing test super user...")
        User.objects.all().delete()
        User.objects.create_superuser('admin', '<EMAIL>', '123456').save()
        print("Created superuser admin/123456")
