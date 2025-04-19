# Django Cloud

## Description
Django Cloud is a django plugin that allows you to add cloud features to your Django applications. It provides simple and easy-to-use interfaces.

## Features
- Service registration
- Service discovery
- Service health check
- Configuration
- Server
- Server Metrics API
- Server Metrics Web UI

## Requirements
- Python3.10 or higher
- Django
- requests
- psutil

## Usage

### Server Example:
```python
# server configuration in settings.py
DJANGO_CLOUD_SERVER = {
    'configuration': {
        'dir': '/var/www/cloud/configurations',
    },
    'metrics': 'web',  # or 'api'
}

# server url in urls.py
from django.urls import path, include

urlpatterns = [
    path('cloud/', include('django_cloud.server.urls'))
]
```

### Service Example:
```python
# service list configuration in settings.py
DJANGO_CLOUD_SERVICES = [{
    'server_list': ["http://127.0.0.1:8000/cloud/"],
    'name': 'service1',
    'key': 'demo1',
    'url': 'http://127.0.0.1:8081/service/',
}]

# service api
from django_cloud import service
services_list = service.get_service('service_name')
# will get:
# [ url1, url2, url3 ]
service.append_extra_information({
    'service_name': {
        'metric1': 1,
        'metric2': 2,
    }})
```

### Service API

- get_service(service_name)
- append_extra_information(data)

### metrics

Server has an ugly frontend at `/metrics/web`.

And, You can get metrics from `/metrics/api` to develop your own frontend.

## Contributing