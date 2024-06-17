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

    def is_reachable(self):
        client = ModbusTcpClient(self.plc.ip_address, self.plc.port)
        connection = client.connect()
        return connection

    def can_connect_to_all_devices(self):
        plc_data = dict()
        status = dict()
        print(self.connected_devices, "connected_devices", len(self.fields))
        mm = ModbusMaster(self.plc, '', {'block_name': 'test'})
        for i in range(len(mm.queries)):
            plc_data.update(mm.read(int(time.time())))
        print("plc_data", plc_data)
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
        return status

    def validate_device(self, device, value_type=None):
        """Validate the device status based on the active power mode and setpoint."""
        self.simulator.set_value(self.plc.name, 'active_power_mode', self.plc.active_power_mode)
        if value_type is not None:
            setpoint = self.plc.value
        else:
            setpoint = 0
        self.simulator.set_value(self.plc.name, 'man_active_power_setpoint', setpoint)
        """sleep for a second before checking if plc was able to write the command"""
        time.sleep(1)
        p_setpoint = self.simulator.get(device.name, self.plc.variable.ahe_name)
        if value_type is not None and p_setpoint != 0:
            return True
        elif value_type is None and p_setpoint == 0:
            return True
        return False

    def get_plc_health_status(self):
        if self.is_reachable():
            read_status = self.can_connect_to_all_devices()
            if all(read_status.values()):
                return True
            else:
                print(f"{self.plc.name} unable to connect to all devices - {read_status}")
                return False
        else:
            print(f"{self.plc.name} is unreachable")

