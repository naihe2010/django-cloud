from django.apps import apps as global_apps

def get_service(service_name):
    _app = global_apps.get_app_config("service")
    sm = _app.service_manager
    return sm.get_service(service_name)


def append_extra_information(extra_information):
    pass