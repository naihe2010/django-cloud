from collections import defaultdict

from django.shortcuts import render
from django.http import JsonResponse
from .models import Service, ServiceState, Hardware, HardwareValue


def web(request):
    return render(request, "django_cloud/metrics.html", {'key': '__all__'})


def __detail(request, key):
    service = Service.objects.get(key=key)
    time_gte = request.GET.get('time_gte', None)
    service_states = ServiceState.objects.filter(service=service)
    if time_gte is None:
        service_states = service_states.order_by('-created_at')
        service_states = service_states[:1]

    else:
        service_states = service_states.filter(created_at__gte=time_gte)

    hw_data = {}
    hw_data['status'] = 'up' if service.is_alive else 'down'
    hw_data['values'] = {}
    values = HardwareValue.objects.filter(state__in=service_states).all()
    hw_names = set([x.hardware.name for x in values])
    for name in hw_names:
        attributes = set([x.hardware.attribute for x in values if x.hardware.name == name])
        hw_data['values'][name] = {x: {} for x in attributes}
        for attribute in attributes:
            hw_ids = set([x.hardware.hw_id for x in values if x.hardware.name == name and x.hardware.attribute == attribute])
            hw_data['values'][name][attribute] = {x: {} for x in hw_ids}
            for hw_id in hw_ids:
                hw_id_values = [x for x in values if x.hardware.name == name and x.hardware.attribute == attribute and x.hardware.hw_id == hw_id]
                data = hw_data['values'][name][attribute][hw_id]
                data['time'] = [x.state.created_at for x in hw_id_values]
                data['unit'] = [x.hardware.unit for x in hw_id_values]
                data['value'] = [x.value for x in hw_id_values]

    return JsonResponse(hw_data)


def api(request):
    if request.method != "GET":
        return JsonResponse({'error': 'method must be get', 'status': 405})

    if request.GET.get('key') is None:
        return JsonResponse({'error':'key is required','status': 400})

    key = request.GET.get('key')
    if key != '__all__':
        return __detail(request, key)

    services = Service.objects.all()
    data = {service.key: {} for service in services}
    for service in services:
        service_states = ServiceState.objects.filter(service=service).order_by('-created_at')[:1]
        if len(service_states) == 0:
            continue

        state = service_states[0]
        hw_data = data[service.key]
        hw_data['status'] = 'up' if service.is_alive else 'down'
        hw_data['time'] = state.time
        hw_data['values'] = {}
        hw_values = HardwareValue.objects.filter(state=state).all()
        hws_names = set([x.hardware.name for x in hw_values])
        for name in hws_names:
            attrbutes = set([x.hardware.attribute for x in hw_values if x.hardware.name == name])
            hw_data['values'][name] = {x: {} for x in attrbutes}
            for attr in attrbutes:
                vs = [x for x in hw_values if x.hardware.name == name and x.hardware.attribute == attr]
                if len(vs) > 0:
                    ivs = [x.value for x in vs]
                    hw_data['values'][name][attr] = {'unit': vs[0].hardware.unit, 'value': sum(ivs) / len(ivs)}

    return JsonResponse(data)
