import json
from django.http import JsonResponse
from .models import Information, Hardware, HardwareValue
from .models import Service, ServiceState, ServiceExtra
from ..state import State


ErrorMethodMustBePost = {'error': 'Method must be POST'}
ErrorInput = {'error': 'Input error'}
ErrorNotFound = {'error': 'Not found'}
ErrorNotActive = {'error': 'Not active'}
ErrorAlreadyRegistered = {'error': 'Already registered'}
OkSuccess = {'success': 'ok'}


def register(request):
    if request.method != 'POST':
        return JsonResponse(ErrorMethodMustBePost, status=405)

    body = json.loads(request.body)
    name = body.get('name')
    key = body.get('key')
    url = body.get('url')
    if name is None or key is None or url is None:
        return JsonResponse(ErrorInput, status=400)

    service = Service.objects.get(name=name, key=key, url=url)
    if service is None:
        return JsonResponse(ErrorNotFound, status=404)

    if service.is_alive:
        return JsonResponse(ErrorAlreadyRegistered, status=409)

    service.is_alive = True
    service.save()
    return JsonResponse(OkSuccess, status=200)

def unregister(request):
    if request.method != 'POST':
        return JsonResponse(ErrorMethodMustBePost, status=405)

    body = json.loads(request.body)
    name = body.get('name')
    key = body.get('key')
    if name is None or key is None:
        return JsonResponse(ErrorInput, status=400)

    service = Service.objects.get(key=key)
    if service is None:
        return JsonResponse(ErrorInput, status=404)

    service.is_alive = False
    service.save()
    return JsonResponse(OkSuccess, status=200)

def information(request):
    if request.method != 'POST':
        return JsonResponse(ErrorMethodMustBePost, status=405)

    body = json.loads(request.body)
    key = body.get('key')
    if key is None:
        return JsonResponse(ErrorInput, status=400)

    service = Service.objects.get(key=key)
    if service is None:
        return JsonResponse(ErrorNotFound, status=404)

    if not service.is_active:
        return JsonResponse(ErrorNotActive, status=409)

    service.is_alive = True
    service.save()
    info = body.get('data')
    obj = Information.objects.create(service=service, info=info)
    obj.save()
    save_state(service, info)
    return JsonResponse(OkSuccess, status=200)


def get_service(request):
    if request.method != 'POST':
        return JsonResponse(ErrorMethodMustBePost, status=405)

    body = json.loads(request.body)
    service_name = body.get('service_name')
    if service_name is None:
        return JsonResponse(ErrorInput, status=404)

    services = Service.objects.filter(name=service_name)
    url_list = [s.url for s in services]
    return JsonResponse({'service_list': url_list}, status=200)


def save_state(service, data):
    state_data = data['data']
    if len(state_data) == 0:
        return

    state = State()
    state.loads(state_data)
    service_state = ServiceState.objects.create(service=service, time=state.time)
    service_state.save()
    for hw in state.hardware:
        (hardware, created) = Hardware.objects.get_or_create(
            service=service,
            name=hw[0],
            hw_id=hw[1],
            attribute=hw[2],
            unit=hw[3],
            range_min=hw[5],
            range_max=hw[6])
        hardware.save()

        if hw[4] is not None:
            value = HardwareValue.objects.create(state=service_state, hardware=hardware, value=hw[4])
            value.save()

    extra = data.get('extra')
    if extra is not None:
        service_extra = ServiceExtra.objects.create(service=service, extra=extra)
        service_extra.save()
