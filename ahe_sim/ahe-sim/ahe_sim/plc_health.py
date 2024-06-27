import time
from pymodbus.client import ModbusTcpClient
from ahe_mb.models import SiteDevice, DeviceMap, Field
from ahe_mb.master import ModbusMaster


class PlcHealth:
    def __init__(self, plc, simulator):
        self.plc = plc
        self.connected_devices = SiteDevice.objects.filter().exclude(name__icontains='ems')
        self.simulator = simulator
        self.fields = list()
        device_map = DeviceMap.objects.filter(device_type=self.plc.device_type)
        for dm in device_map:
            self.fields.append(Field.objects.filter(map=dm.map))

    def get_plc_data(self):
        plc_data = dict()
        mm = ModbusMaster(self.plc, '', {'block_name': 'test'})
        for i in range(len(mm.queries)):
            plc_data.update(mm.read(int(time.time())))
            print("plc_data", plc_data, len(mm.queries))
        return plc_data

    def can_connect_to_all_devices(self):
        plc_data = self.get_plc_data()
        status = dict()
        for dev in self.connected_devices:
            status[f"{dev.name}"] = None
            if f"{self.plc.name}_{dev.name}_status" in plc_data and \
                    plc_data[f"{self.plc.name}_{dev.name}_status"] == 1:
                status[f"{dev.name}"] = True
            elif f"{dev.name}_status" not in plc_data:
                status[f"{dev.name}"] = False
            elif f"{dev.name}_status" in plc_data and \
                    plc_data[
                        f"{self.plc.name}_{dev.name}_status"] == 0:
                status[f"{dev.name}"] = False
            elif 'ems_1_modbus_failed' in plc_data:
                status['ems_1'] = False
        return status

    def get_plc_health_status(self):
        read_status = self.can_connect_to_all_devices()
        if all(read_status.values()):
            return True
        elif 'ems' in read_status and read_status['ems_1'] == False:
            print(f"{self.plc.name} is not reachable")
            return False
        else:
            print(f"{self.plc.name} unable to connect to devices - {read_status}")
            return False
