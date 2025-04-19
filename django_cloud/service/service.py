import json
import threading
import time
import requests
from django.conf import settings
from ..state import State


class ServerNode(object):
    def __init__(self, server):
        self.__server = server
        self.__registered = False
        self.__failed = 0
        self.__last = 0

    def is_registered(self):
        return self.__registered

    def set_registered(self, registered):
        self.__registered = registered

    def on_failed(self):
        self.__failed += 1

    def update(self):
        self.__last = time.time()

    def reset(self):
        self.__failed = 0

    def need_information(self, now, interval):
        return now - self.__last > interval

    def failed_too_much(self, max_failed):
        return self.__failed > max_failed


class Service(object):
    def __init__(self, conf):
        self.__stop_event = threading.Event()
        self.__stop_event.set()
        self.__server_list = conf['server_list']
        self.__name = conf['name']
        self.__key = conf['key']
        self.__url = conf['url']
        # Optional attributes
        self.__interval = conf.get('interval', 10)
        self.__max_failed = conf.get('max_failed', 3)
        # Runtime variables
        self.__registered_servers = {s: ServerNode(s) for s in self.__server_list}
        self.__state = State()
        self.__data = ''
        self.__extra_data = ''

    def __server_node(self, server):
        return self.__registered_servers[server]

    def __register(self, server, node):
        ret = self.do_register(server, self.__name, self.__key, self.__url)
        node.set_registered(ret)
        node.update()
        if ret is True:
            node.reset()

    def __unregister(self, server, node):
        node.set_registered(False)
        self.do_unregister(server, self.__name, self.__key)

    def __information(self, server, node):
        ret = self.do_information(server, self.__name, self.__key,
                                  {'data': self.__data,
                                   'extra': self.__extra_data})
        node.update()
        if ret is True:
            node.reset()

        else:
            node.on_failed()

    def __process(self, server):
        node = self.__server_node(server)
        now = time.time()
        if node.is_registered() is False:
            self.__register(server, node)

        elif node.need_information(now, self.__interval):
            self.__information(server, node)

        if node.failed_too_much(self.__max_failed):
            self.__unregister(server, node)

    def run(self):
        while not self.__stop_event.is_set():
            time_begin = time.time()
            self.__state.reset()
            self.__state.collect()
            self.__data = self.__state.dumps(beautiful=False)
            time_end = time.time()
            need = time_end - time_begin - self.__interval
            if need > 0:
                time.sleep(need)

            for server in self.__server_list:
                self.__process(server)

    def start(self):
        if not self.__stop_event.is_set():
            return

        self.__stop_event.clear()
        threading.Thread(target=self.run, daemon=True).start()

    def stop(self):
        self.__stop_event.set()

    def get_service(self, service_name):
        service_list = []
        for server in self.__server_list:
            node = self.__server_node(server)
            if node.is_registered():
                _list = self.do_get_service(server, service_name)
                service_list.extend(_list)

        return service_list

    def __http_post(self, url, data):
        json_data = json.dumps(data)
        try:
            res = requests.post(url,
                                data=json_data,
                                headers={'Content-Type': 'application/json'})
            return res

        except Exception as e:
            print(e)
            return None

    def do_register(self, server, name, key, url):
        res = self.__http_post(server + 'register/',
                              { 'name': name,
                                'key': key, 'url': url})
        return res is not None \
            and (res.status_code == 200
                 or res.status_code == 409)

    def do_unregister(self, server, name, key):
        self.__http_post(server + 'unregister/',
                         { 'name': name, 'key': key})

    def do_information(self, server, name, key, data):
        res = self.__http_post(server + 'information/',
                               {'name': name,
                                'key': key, 'data': data})
        return res is not None and res.status_code == 200

    def do_get_service(self, server, service_name):
        res = self.__http_post(server + 'get_service/',
                               {'service_name': service_name})
        if res is None or res.status_code != 200:
            return []

        data = res.json()
        return data['service_list']


class ServiceManager(object):
    def __init__(self):
        self.__services = [Service(conf) for conf in settings.DJANGO_CLOUD_SERVICES]

    def start(self):
        print("Django Cloud Service starting")
        for service in self.__services:
            service.start()

    def stop(self):
        print("Django Cloud Service stopping")
        for service in self.__services:
            service.stop()

    def get_service(self, service_name):
        service_list = []
        for service in self.__services:
            _list = service.get_service(service_name)
            service_list.extend(_list)

        service_set = set(service_list)
        return list(service_set)