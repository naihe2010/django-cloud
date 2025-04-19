import time
import datetime
from collections import namedtuple
import psutil
import json


Hardware = namedtuple('Hardware', ['name', 'hw_id', 'attribute', 'unit', 'value', 'value_min', 'value_max',])


class State(object):
    def __init__(self):
        self.service = ""
        self.reset()

    def reset(self):
        self.time = datetime.datetime.now()
        self.hardware = []

    def dumps(self, beautiful=False):
        level = 4 if beautiful else None
        return json.dumps({'service': self.service,
                           'time': self.time.isoformat(),
                           'hardware': self.hardware},
                          indent=level)

    def loads(self, data):
        json1 = json.loads(data)
        self.service = json1['service']
        self.time = datetime.datetime.fromisoformat(json1['time'])
        self.hardware = json1['hardware']

    def collect(self):
        self.collect_cpu()
        self.collect_memory()
        self.collect_disk()
        self.collect_network()
        return self

    def collect_cpu(self):
        cpu = psutil.cpu_percent(interval=1, percpu=True)
        for i, c in enumerate(cpu):
            temp = psutil.sensors_temperatures().get('cpu_thermal')
            self.hardware.append(Hardware(name='cpu', hw_id=i, attribute='usage', unit='%', value=c, value_min=0, value_max=0))
            self.hardware.append(Hardware(name='cpu', hw_id=i, attribute='temp', unit='', value=temp, value_min=0, value_max=0))

    def collect_memory(self):
        mem = psutil.virtual_memory()
        self.hardware.append(Hardware(name='memory', hw_id='memory', attribute='usage', unit='%', value=mem.percent, value_min=0, value_max=0))
        swap = psutil.swap_memory()
        self.hardware.append(Hardware(name='memory', hw_id='swap', attribute='usage', unit='%', value=swap.percent, value_min=0, value_max=0))

    def collect_disk(self):
        partitions = psutil.disk_partitions()
        for partition in partitions:
            disk = psutil.disk_usage(partition.mountpoint)
            temp = psutil.sensors_temperatures().get(partition.device)
            self.hardware.append(Hardware(name='disk', hw_id=partition.mountpoint, attribute='usage', unit='%', value=disk.percent, value_min=0, value_max=0))
            self.hardware.append(Hardware(name='disk', hw_id=partition.mountpoint, attribute='temp', unit='', value=temp, value_min=0, value_max=0))

    def collect_network(self):
        net_stats = psutil.net_if_stats()
        psutil.net_io_counters.cache_clear()
        ni_counters1 = psutil.net_io_counters(pernic=True)
        time.sleep(1)
        ni_counters2 = psutil.net_io_counters(pernic=True)
        for nic, stats in net_stats.items():
            if nic == 'lo' or stats.isup is False:
                continue

            counters1 = ni_counters1.get(nic)
            counters2 = ni_counters2.get(nic)
            if counters1 and counters2:
                send_bytes = counters2.bytes_sent - counters1.bytes_sent
                recv_bytes = counters2.bytes_recv - counters1.bytes_recv
                send_value = send_bytes / (1024.0 * 1024)
                recv_value = recv_bytes / (1024.0 * 1024)
                self.hardware.append(Hardware(name='network', hw_id=nic, attribute='sent', unit='M', value=send_value, value_min=0, value_max=stats.speed))
                self.hardware.append(Hardware(name='network', hw_id=nic, attribute='recv', unit='M', value=recv_value, value_min=0, value_max=stats.speed))

if __name__ == '__main__':
    state = State()
    state.collect()
    print(state.dumps(beautiful=True))