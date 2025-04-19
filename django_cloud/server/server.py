import time
import threading
from django.conf import settings
#from .models import Service


class Server(object):
    def __init__(self):
        self.__stop_event = threading.Event()
        self.__stop_event.set()
        self.__timeout = settings.DJANGO_CLOUD_SERVER.get('timeout', 60)

    def start(self):
        print("Starting Django Cloud Server")
        if not self.__stop_event.is_set():
            return

        self.__stop_event.clear()
        threading.Thread(target=self.__run).start()

    def stop(self):
        print("Stopping Django Cloud Server")
        self.__stop_event.set()

    def __run(self):
        while not self.__stop_event.is_set():
            time.sleep(1)
            self.__check_services()

    def __check_services(self):
        from .models import Service
        now = time.time()
        services = Service.objects.filter(is_alive=True)
        for service in services:
            updated_at = service.updated_at.timestamp()
            if now - updated_at > self.__timeout:
                print("client {} has expired".format(service.key))
                service.is_alive = False
                service.save()

