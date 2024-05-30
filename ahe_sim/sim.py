import time
from ahe_mb.models import Map, Field, SiteDevice, DeviceMap
from ahe_mb.variable import ModbusVar
from slave import run_slave
import threading
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext


class Simulation:
    def __init__(self):
        self.server_context = {}
        self.get_field_dict = {}
        self.field_dict = {}
        self.map_names = [m.name for m in Map.objects.filter()]
        self.slaves = {}
        self.data = {}
        self.maps = {}
        self.i = 1
        self.threads = []
        self.devices = dict()

    def set_server_context(self, server_identity, data_block_size):
        data_block = ModbusSequentialDataBlock(0, [0] * data_block_size)
        store = ModbusSlaveContext(hr=data_block)
        self.server_context[server_identity] = ModbusServerContext(slaves=store, single=True)
        self.slaves[server_identity] = store

    def set_all_initial_values_to_0(self, server_identity):
        if server_identity not in self.data:
            self.data[server_identity] = dict()
        field_addresses = self.field_dict[server_identity].keys()
        for i in field_addresses:
            self.slaves[server_identity].setValues(3, i, [0])
        for address, name in self.field_dict[server_identity].items():
            self.data[server_identity][name] = \
                self.slaves[server_identity].getValues(3, address, count=1)[0]
        return self.data

    def get_values(self, server_identity, map_name, name):
        address = self.get_field_dict[server_identity][name]
        value = self.slaves[server_identity].getValues(3, address.field_address, count=1)[0]
        self.data[server_identity][f"{map_name}_{name}"] = value
        return value

    def set_value(self, server_identity, ahe_name, value):
        field = self.get_field_dict[server_identity][ahe_name]
        register_address = field.field_address
        modbus_var = ModbusVar(field)
        modbus_var.set_value(value)
        self.slaves[server_identity].setValues(3, register_address, modbus_var.registers)
        self.data[server_identity][f"{field.ahe_name}"] = \
            self.slaves[server_identity].getValues(3, register_address, count=1)[0]
        print(f"Value set for {server_identity} for {field.ahe_name} with {modbus_var.registers}")

    def update_and_translate_values(self, server_identity, ahe_name, value):
        self.set_value(server_identity, ahe_name, value)

    def initialize_servers(self):
        try:
            config_objects = SiteDevice.objects.all()
            devices_by_port = {}
            for config_obj in config_objects:
                port = config_obj.port
                if port not in devices_by_port:
                    devices_by_port[port] = []
                devices_by_port[port].append(config_obj)
            print("devices by port", devices_by_port)
            for port, config_objects in devices_by_port.items():
                for config_obj in config_objects:
                    device_name = config_obj.name
                    device_type = config_obj.device_type
                    for device_map in DeviceMap.objects.filter(device_type=device_type):
                        if device_name not in self.devices:
                            self.devices[device_name] = list()
                        if device_name not in self.field_dict:
                            self.field_dict[device_name] = dict()
                        if device_name not in self.get_field_dict:
                            self.get_field_dict[device_name] = dict()
                        self.devices[device_name].append(device_map.map)
                        fields = Field.objects.filter(map=device_map.map)
                        for f in fields:
                            self.field_dict[device_name][f.field_address] = f.ahe_name
                            self.get_field_dict[device_name][f.ahe_name] = f
                    self.threads.append((device_name, port))
        except Exception as e:
            print(f"Error setting up simulation: {e}")

    def start_server(self, device_name, timeout=None):
        for device, port in self.threads:
            if device == device_name:
                if timeout:
                    time.sleep(timeout)
                data_block_size = max(self.field_dict[device_name].keys()) + 1
                self.set_server_context(device_name, data_block_size)
                self.set_all_initial_values_to_0(device_name)
                print(f"start server for {device_name} {port}")
                thread = threading.Thread(target=run_slave,
                                          args=(self.server_context[device_name], port, device_name))
                thread.start()
