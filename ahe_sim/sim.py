from ahe_mb.models import Map, Field, SiteDevice, DeviceMap
from ahe_mb.variable import ModbusVar
from slave import run_slave
import threading
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext




class Simulation:
    def __init__(self):
        self.server_context = {}
        self.get_field_dict = {}
        self.buffer_check_timer = None
        self.field_dict = {}
        self.device = {}
        self.map_names = [m.name for m in Map.objects.filter()]
        self.slaves = {}
        self.data = {}
        self.buffer = list()
        self.maps = {}
        self.i = 1
        self.threads = []
        self.devices = dict()

    def set_context(self, server_identity, data_block_size):
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

    def get_values(self,server_identity,map_name, name):
        address = self.get_field_dict[server_identity][name]
        value =self.slaves[server_identity].getValues(3, address.field_address, count=1)[0]
        self.data[server_identity][f"{map_name}_{name}"] = value
        return value

    def set_value_to_address(self, server_identity, ahe_name, value):
        field = self.get_field_dict[server_identity][ahe_name]
        register_address = field.field_address
        modbus_var = ModbusVar(field)
        modbus_var.set_value(value)
        self.slaves[server_identity].setValues(3, register_address, modbus_var.registers)
        self.data[server_identity][f"{field.ahe_name}"] = \
            self.slaves[server_identity].getValues(3, register_address, count=1)[0]
        print(f"Value set for {server_identity} for {field.ahe_name} with {modbus_var.registers}")

    def update_and_translate_values(self, server_identity, ahe_name, value):
        self.set_value_to_address(server_identity, ahe_name, value)

    def pop_buffer_item(self, server_identity_key, item):
        ahe_name = list(item[server_identity_key].keys())[0]
        value = item[server_identity_key][ahe_name]
        self.update_and_translate_values(server_identity_key, ahe_name, value)
        self.buffer.remove(item)
        if server_identity_key in self.data:
            map_name = self.devices[server_identity_key]
            self.data[server_identity_key][f"{map_name}_{ahe_name}"] = value


    def start_server(self):
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
                    map_obj = DeviceMap.objects.filter(device_type=device_type)[0].map
                    map_name = map_obj.name
                    if map_name not in self.map_names:
                        print(f"{map_name} is not a valid map name.")
                        continue
                    if device_name not in self.devices:
                        self.devices[device_name] = list()
                    self.device[device_name] = port
                    self.devices[device_name] = map_obj
                    fields = Field.objects.filter(map=map_obj)
                    if device_name not in self.field_dict:
                        self.field_dict[device_name] = dict()
                    if device_name not in self.get_field_dict:
                        self.get_field_dict[device_name] = dict()
                    for f in fields:
                        self.field_dict[device_name][f.field_address] = f.ahe_name
                        self.get_field_dict[device_name][f.ahe_name] = f
            for device_name, port in self.device.items():
                data_block_size = max(self.field_dict[device_name].keys()) + 1
                self.set_context(device_name, data_block_size)
                self.set_all_initial_values_to_0(device_name)
                thread = threading.Thread(target=run_slave,
                                  args=(self.server_context[device_name], port, device_name,))
                thread.start()
                print(f"server started for {device_name} {port}")
        except Exception as e:
            print(f"Error setting up simulation: {e}")

