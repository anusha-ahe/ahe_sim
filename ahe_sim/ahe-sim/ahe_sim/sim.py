import time
from ahe_mb.models import Map, Field, SiteDevice, DeviceMap
from ahe_mb.variable import ModbusVar
from ahe_sim.slave import run_slave
import multiprocessing
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

class Simulation:
    def __init__(self):
        self.server_processes = {}
        self.server_context = {}
        self.get_field_dict = {}
        self.address_to_field = {}
        self.slaves = {}
        self.data = {}
        self.processes = []
        self.devices = dict()
        self.initialize_servers()

    def set_all_initial_values_to_0(self, device):
        if device not in self.data:
            self.data[device] = dict()
        field_addresses = self.address_to_field[device].keys()
        for i in field_addresses:
            self.slaves[device].setValues(3, i, [0])
        for address, name in self.address_to_field[device].items():
            self.data[device][name] = \
                self.slaves[device].getValues(3, address, count=1)[0]
        return self.data

    def initialize_servers(self):
        devices_by_port = {}
        try:
            device_objects = SiteDevice.objects.all()
            for device_obj in device_objects:
                port = device_obj.port
                if port not in devices_by_port:
                    devices_by_port[port] = list()
                devices_by_port[port].append(device_obj)
            print("devices by port", devices_by_port)
            for port, device_objects in devices_by_port.items():
                for device_obj in device_objects:
                    device_name = device_obj.name
                    for device_map in DeviceMap.objects.filter(device_type=device_obj.device_type):
                        if not device_name in self.devices:
                            self.devices[device_name] = []
                        self.address_to_field.setdefault(device_name, {})
                        self.get_field_dict.setdefault(device_name, {})
                        self.devices[device_name].append(device_map.map)
                        fields = Field.objects.filter(map=device_map.map)
                        for f in fields:
                            self.address_to_field[device_name][f.field_address] = f.ahe_name
                            self.get_field_dict[device_name][f.ahe_name] = f
                    self.processes.append((device_name, port))
        except Exception as e:
            print(f"Error setting up simulation: {e}")

    def set_server_context(self, device, data_block_size):
        data_block = ModbusSequentialDataBlock(0, [0] * data_block_size)
        store = ModbusSlaveContext(hr=data_block)
        self.server_context[device] = ModbusServerContext(slaves=store, single=True)
        self.slaves[device] = store

    def get(self, device,name):
        address = self.get_field_dict[device][name]
        value = self.slaves[device].getValues(3, address.field_address, count=1)[0]
        self.data[device][name] = value
        return value

    def set_value(self, device, ahe_name, value):
        field = self.get_field_dict[device][ahe_name]
        register_address = field.field_address
        print("reg address", register_address)
        modbus_var = ModbusVar(field)
        modbus_var.set_value(value)
        self.slaves[device].setValues(3, register_address, modbus_var.registers)
        self.data[device][f"{field.ahe_name}"] = \
            self.slaves[device].getValues(3, register_address, count=1)[0]
        print(f"Value set for {device} for {field.ahe_name} with {modbus_var.registers}")

    def update_and_translate_values(self, device, ahe_name, value):
        self.set_value(device, ahe_name, value)

    def start_server(self, device_name, timeout=None):
        print("process", self.processes)
        for device, port in self.processes:
            if device == device_name:
                if timeout:
                    time.sleep(timeout)
                data_block_size = max(self.address_to_field[device_name].keys()) + 1
                self.set_server_context(device_name, data_block_size)
                self.set_all_initial_values_to_0(device_name)
                print(f"start server for {device_name} {port}")
                process = multiprocessing.Process(target=run_slave, args=(self.server_context[device_name], port, device_name))
                process.start()
                print(f"started server for {device_name} {port}")
                self.server_processes.setdefault(device_name, [])
                self.server_processes[device_name].append(process)

    def stop_server(self, device_name):
        if device_name not in self.server_processes:
            print(f"No server running for {device_name}.")
            return
        processes = self.server_processes[device_name]
        for proc in processes:
            print(f"process to stop {proc}")
            proc.terminate()
            proc.join()
            print(f"Server for {device_name} stopped.")
        del self.server_processes[device_name]

