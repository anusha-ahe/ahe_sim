from ahe_translate import Translate
from ahe_mb.models import Map, Field
from ahe_mb.variable import ModbusVar
from slave import run_slave
from ahe_sim.models import SimulatorConfig
import threading
from ahe_translate.models import Config
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

config = Config.objects.get(id=1)


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
        self.map = dict()

    def set_context(self, server_identity, data_block_size):
        data_block = ModbusSequentialDataBlock(0, [0] * data_block_size)
        store = ModbusSlaveContext(hr=data_block)
        self.server_context[server_identity] = ModbusServerContext(slaves=store, single=True)
        self.slaves[server_identity] = store

    def set_all_initial_values_to_0(self, map_obj, server_identity):
        map_name = map_obj.name
        self.data[server_identity] = dict()
        field_addresses = self.field_dict[server_identity].keys()
        for i in field_addresses:
            self.slaves[server_identity].setValues(3, i, [0])
        for address, name in self.field_dict[server_identity].items():
            self.data[server_identity][f"{map_name}_{name}"] = \
                self.slaves[server_identity].getValues(3, address, count=1)[0]
        return self.data

    def get_values(self,server_identity,map_name, name):
        address = self.get_field_dict[server_identity][name]
        value =self.slaves[server_identity].getValues(3, address.field_address, count=1)[0]
        self.data[server_identity][f"{map_name}_{name}"] = value
        return value

    def set_value_to_address(self, server_identity, ahe_name, value):
        map_name = self.maps[server_identity]
        field = self.get_field_dict[server_identity][ahe_name]
        register_address = field.field_address
        modbus_var = ModbusVar(field)
        modbus_var.set_value(value)
        self.slaves[server_identity].setValues(3, register_address, modbus_var.registers)
        self.data[server_identity][f"{map_name}_{field.ahe_name}"] = \
            self.slaves[server_identity].getValues(3, register_address, count=1)[0]
        print(f"Value set for {map_name} for {field.ahe_name} with {modbus_var.registers}")

    def update_and_translate_values(self, server_identity, ahe_name, value):
        self.set_value_to_address(server_identity, ahe_name, value)
        translate = Translate(config)
        translated_data = translate.write(self.data[server_identity])
        difference = {k: translated_data.get(k) for k in self.data[server_identity] if
                      translated_data.get(k) != self.data[server_identity][k]}
        for key, value in difference.items():
            ahe_name = key.split(f"{self.maps[server_identity]}_")[-1]
            self.set_value_to_address(server_identity, ahe_name, value)


    def pop_buffer_item(self, server_identity_key, item):
        ahe_name = list(item[server_identity_key].keys())[0]
        value = item[server_identity_key][ahe_name]
        self.update_and_translate_values(server_identity_key, ahe_name, value)
        self.buffer.remove(item)
        if server_identity_key in self.data:
            map_name = self.maps[server_identity_key]
            self.data[server_identity_key][f"{map_name}_{ahe_name}"] = value


    def start_server(self):
        try:
            config_objects = SimulatorConfig.objects.all()
            for config_obj in config_objects:
                map_obj = config_obj.map_name
                map_name = map_obj.name
                if map_name not in self.map:
                    self.map[map_name] = list()
                port = config_obj.port
                if map_name not in self.map_names:
                    print(f"{map_name} is not a valid map name.")
                    continue
                server_identity = f"{map_name}_{self.i}"
                self.device[server_identity] = port
                fields = Field.objects.filter(map=map_obj)
                self.field_dict[server_identity] = {f.field_address: f.ahe_name for f in fields}
                self.get_field_dict[server_identity] = {f.ahe_name: f for f in fields}
                data_block_size = max(self.field_dict[server_identity].keys()) + 1
                self.set_context(server_identity, data_block_size)
                self.set_all_initial_values_to_0(map_obj, server_identity)
                self.maps[server_identity] = map_name
                self.map[map_name].append(server_identity)
                thread = threading.Thread(target=run_slave,
                                          args=(self.server_context[server_identity], port, map_name,))
                thread.start()
                self.threads.append(thread)
                self.i += 1
        except Exception as e:
            print(f"Error setting up simulation: {e}")

