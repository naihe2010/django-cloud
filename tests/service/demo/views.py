from django_cloud.service import get_service
from django.http.response import JsonResponse

def index(request):
    return JsonResponse({'index': 'hello world'})

def hello(request):
    return JsonResponse({'hello': 'world'})

def world(request):
    return JsonResponse({'world': 'hello'})

def service(request):
    service_list = get_service("service1")
    return JsonResponse({'service_name': 'service1',
                         'service_list': service_list})
