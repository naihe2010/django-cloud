from django.db import models


class Service(models.Model):
    id = models.AutoField(primary_key=True)

    # base attributes
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    url = models.CharField(max_length=1024)

    # runtime attributes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_alive = models.BooleanField(default=False)

    # configuration attributes
    config_path = models.CharField(max_length=1024)

    def __str__(self):
        return '{}:{}'.format(self.name, self.key)


class Information(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    info = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ServiceState(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    time = models.DateTimeField()

    def __str__(self):
        return '{} {}'.format(self.service, self.time)


class Hardware(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    # Key
    name = models.CharField(blank=False, max_length=64)
    hw_id = models.CharField(blank=False, max_length=32)
    attribute = models.CharField(blank=False, max_length=64)
    # Optional
    unit = models.CharField(default='%', max_length=32)
    range_min = models.FloatField(default=0.0)
    range_max = models.FloatField(default=100.0)


class HardwareValue(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.ForeignKey(ServiceState, on_delete=models.CASCADE)
    hardware = models.ForeignKey(Hardware, on_delete=models.CASCADE)
    value = models.FloatField()

    def __str__(self):
        return '{} {} {} {}'.format(self.state,
                                    self.hardware.name,
                                    self.hardware.hw_id,
                                    self.value)


class ServiceExtra(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    extra = models.TextField()

    def __str__(self):
        return '{} {}'.format(self.service, self.extra)
