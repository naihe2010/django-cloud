from django.contrib import admin
from .models import Information, Hardware, HardwareValue
from .models import Service, ServiceState, ServiceExtra


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'url', 'is_active', 'is_alive', 'config_path', 'updated_at')
    list_editable = ('is_active',)


class DeleteOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Information)
class InformationAdmin(DeleteOnlyAdmin):
    list_display = ('service', 'info')


@admin.register(ServiceState)
class StateAdmin(DeleteOnlyAdmin):
    list_display = ('service', 'time', 'values')

    def values(self, obj):
        return obj.hardwarevalue_set.all()


@admin.register(HardwareValue)
class HardwareValueAdmin(DeleteOnlyAdmin):
    list_display = ('service', 'state', 'name', 'hw_id', 'attribute', 'unit', 'value')

    def service(self, obj):
        return obj.hardware.service

    def name(self, obj):
        return obj.hardware.name

    def attribute(self, obj):
        return obj.hardware.attribute

    def hw_id(self, obj):
        return obj.hardware.hw_id

    def unit(self, obj):
        return obj.hardware.unit


@admin.register(ServiceExtra)
class ExtraAdmin(DeleteOnlyAdmin):
    list_display = ('service', 'extra')
