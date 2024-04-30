import subprocess
import threading
import cmd
import time
from ahe_translate import Translate
from pymodbus.server.async_io import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from ahe_mb.models import Map, Field
from ahe_translate.models import Config
from ahe_mb.variable import ModbusVar



def is_server_running(port):
    cmd = f"netstat -tln | grep {ip}:{port}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

config = Config.objects.get(id=1)

buffer_check_interval = 1
ip = 'localhost'
def run_slave(server_context, port, name):
    identity = ModbusDeviceIdentification()
    if is_server_running(port):
        print(f"Server for map {name} is already running @ {ip}:{port}")
        return
    try:
        print(f"Starting server for map {name} @ {ip}:{port}")
        StartTcpServer(context=server_context, identity=identity, address=(ip, port))
    except Exception as e:
        print(f"Failed to start server for map {name}: {e}")
    else:
        print(f"Started server for map {name} @ {ip}:{port}")

class ModbusSlaveCmd(cmd.Cmd):
    intro = 'Simulator Setup\n'
    prompt = 'sim> '

    def __init__(self):
        super().__init__()
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
        self.start_buffer_check_timer()
        self.i = 0

    def set_initial_values(self, map_obj, server_identity):
        map_name = map_obj.name
        self.data[server_identity] = dict()
        field_addresses = self.field_dict[server_identity].keys()
        field_names = self.field_dict[server_identity].values()
        print(field_addresses)
        print(field_names)
        for i in field_addresses:
            self.slaves[server_identity].setValues(3, i, [0])
        for address, name in self.field_dict[server_identity].items():
            self.data[server_identity][f"{map_name}_{name}"] = self.slaves[server_identity].getValues(3, address, count=1)[0]
        print(self.data)
        return self.data

    def set_value_to_address(self, server_identity, ahe_name, value):
        print(ahe_name, server_identity)
        map_name = self.maps[server_identity]
        print(map_name)
        print(self.get_field_dict[server_identity])
        field = self.get_field_dict[server_identity][ahe_name]
        register_address = field.field_address
        modbus_var = ModbusVar(field)
        modbus_var.set_value(value)
        self.slaves[server_identity].setValues(3, register_address, modbus_var.registers)
        self.data[server_identity][f"{map_name}_{field.ahe_name}"] = self.slaves[server_identity].getValues(3, register_address, count=1)[0]
        print(f"Value set for {map_name} for {field.ahe_name} with {modbus_var.registers}")

    def update_and_translate_values(self, server_identity, ahe_name,  value):
        self.set_value_to_address(server_identity, ahe_name, value)
        translate = Translate(config)
        translated_data = translate.write(self.data[server_identity])
        difference = {k: translated_data.get(k) for k in self.data[server_identity] if
                      translated_data.get(k) != self.data[server_identity][k]}
        for key, value in difference.items():
            ahe_name = key.split(f"{self.maps[server_identity]}_")[-1]
            self.set_value_to_address(server_identity, ahe_name, value)

    def do_set(self, arg):
        delay = None
        args = arg.split()
        if len(args) != 3 and len(args) != 4:
            print("Usage: set <map> <ahe_name> <value> or set <map> <ahe_name> <value> <delay>")
            return
        try:
            server_identity = args[0]
            ahe_name = args[1]
            value = float(args[2])
            if len(args) == 4:
                delay = int(args[3])
        except ValueError:
            print("Invalid argument(s).")
            return

        if server_identity not in self.slaves:
            print(f"Map {server_identity}  server not started")
            return
        if ahe_name not in self.field_dict[server_identity].values():
            print(f"Field {ahe_name} not present in map {server_identity}.")
            return
        if not delay:
            print(f"Value setting for {server_identity} at {ahe_name}")
            self.update_and_translate_values(server_identity, ahe_name, value)
        else:
            print(f"Value setting for {server_identity} at {ahe_name}  with {value} in {delay} seconds")
            self.buffer.append({server_identity: {ahe_name: value, "epoch": time.time() + delay}})

    def start_buffer_check_timer(self):
        self.buffer_check_timer = threading.Timer(buffer_check_interval, self.check_buffer)
        self.buffer_check_timer.start()

    def check_buffer(self):
        buffer_copy = self.buffer[:]
        for item in buffer_copy:
            server_identity_key = list(item.keys())[0]
            if time.time() >= item[server_identity_key]["epoch"]:
                self.pop_buffer_item(server_identity_key, item)
        self.start_buffer_check_timer()

    def pop_buffer_item(self, server_identity_key, item):
        ahe_name = list(item[server_identity_key].keys())[0]
        value = item[server_identity_key][ahe_name]
        self.update_and_translate_values(server_identity_key, ahe_name, value)
        self.buffer.remove(item)
        if server_identity_key in self.data:
            map_name = self.maps[server_identity_key]
            self.data[server_identity_key][f"{map_name}_{ahe_name}"] = value

    def complete_set(self, text, line, begidx, endidx):
        arg = line.split()
        completions = []
        if len(arg) == 2:
            completions.extend(filter(lambda x: x.startswith(text), list(self.maps.keys())))
        if len(arg) == 3:
            map_name = arg[1]
            map_obj = Map.objects.filter(name=self.maps[map_name]).first()
            if map_obj:
                field_names = [f.ahe_name for f in Field.objects.filter(map=map_obj)]
                completions.extend(filter(lambda x: x.startswith(text), field_names))

        return completions

    def set_context(self, server_identity, data_block_size):
        data_block = ModbusSequentialDataBlock(0, [0] * data_block_size)
        store = ModbusSlaveContext(hr=data_block)
        self.server_context[server_identity] = ModbusServerContext(slaves=store, single=True)
        self.slaves[server_identity] = store


    def do_start(self, arg):
        print("Starting Simulation Setup ....")
        num_slaves_str = input("Enter the number of Modbus slave servers to start: ")
        try:
            num_slaves = int(num_slaves_str)
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
            return
        for i in range(num_slaves):
            map_name = input(f"Enter the map for {i + 1} device: ")
            if map_name not in self.map_names:
                print(f"{map_name} is not a valid map name.")
                continue
            port_str = input(f"Enter the port number for {map_name}: ")
            try:
                port = int(port_str)
            except ValueError:
                print("Invalid input. Please enter a valid integer for the port number.")
                continue
            server_identity = f"{map_name}_{self.i}"
            self.device[server_identity] = port
            map_obj = Map.objects.filter(name=map_name).first()
            if map_obj:
                fields = Field.objects.filter(map=map_obj)
                self.field_dict[server_identity] = {f.field_address: f.ahe_name for f in fields}
                self.get_field_dict[server_identity] = {f.ahe_name : f for f in fields}
                data_block_size = max(self.field_dict[server_identity].keys())+1
                self.set_context(server_identity, data_block_size)
                self.set_initial_values(map_obj, server_identity)
                self.maps[server_identity] = map_name
                thread = threading.Thread(target=run_slave, args=(self.server_context[server_identity], port, map_name,))
                thread.start()
                print(f"Modbus slave servers started successfully for {map_name}.")
            else:
                print(f"Error: Map {map_name} not found in the database.")
            self.i += 1

if __name__ == "__main__":
    modbus_cmd = ModbusSlaveCmd()
    modbus_cmd.cmdloop()