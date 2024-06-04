import cmd
import csv
import threading
import time
import os
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from ahe_mb.models import Map, Field
from ahe_mb.variable import ModbusVar
from ahe_translate import Translate
from ahe_translate.models import Config
from ahe_sim.slave import run_slave

config = Config.objects.get(id=1)

buffer_check_interval = 1
ip = '0.0.0.0'


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
        self.i = 1
        self.check_config()
        self.threads = []

    def check_config(self):
        files = os.listdir("../config/")
        csv_files = [file.split(".csv")[0] for file in files if file.endswith('.csv')]
        for i in csv_files:
            if i not in self.map_names and i != "config":
                print(f"devices for file {i} does not exist")

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

    def set_initial_config(self, map_name, server_identity):
        csv_file_path = f"config/{map_name}.csv"
        if os.path.isfile(csv_file_path):
            with open(csv_file_path, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.set_value_to_address(server_identity, row['variable'], float(row['value']))
        else:
            print(f"initial config file for {map_name} not present")

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

    def do_set(self, arg):
        delay = None
        args = arg.split()
        if len(args) != 3 and len(args) != 4:
            print("Usage: set <devices> <ahe_name> <value> or set <devices> <ahe_name> <value> <delay>")
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
            print(f"Field {ahe_name} not present in devices {server_identity}.")
            return
        if not delay:
            print(f"Value setting for {server_identity} at {ahe_name}")
            self.update_and_translate_values(server_identity, ahe_name, value)
        else:
            print(f"Value setting for {server_identity} at {ahe_name}  with {value} in {delay} seconds")
            self.buffer.append({server_identity: {ahe_name: value, "epoch": time.time() + delay}})

    def do_setr(self, arg):
        args = arg.split()
        if len(args) != 5 and len(args) != 4:
            print("Usage: set <devices> <ahe_name> <[value_list]> <duration> <interval>")
            return
        try:
            server_identity = args[0]
            ahe_name = args[1]
            value = eval(args[2])
            duration = int(args[3])
            interval = args[4] if len(args) == 5 else None
            if interval is None:
                interval_size = len(value)
                interval_list = [interval_size * i for i in range(duration)]
            else:
                interval = int(interval)
                interval_list = list(range(0, duration + interval, interval))
            if server_identity not in self.slaves:
                print(f"Map {server_identity}  server not started")
                return
            if ahe_name not in self.field_dict[server_identity].values():
                print(f"Field {ahe_name} not present in devices {server_identity}.")
                return
            self.update_and_translate_values(server_identity, ahe_name, value[0])

            for i in range(1, len(value)):
                self.buffer.append({server_identity: {ahe_name: value[i], "epoch": time.time() + interval_list[i]}})
        except ValueError:
            print("Invalid argument(s).")
            return

    def complete_setr(self, text, line, begidx, endidx):
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

    def do_start(self, arg):
        print("Starting Simulation Setup ....")
        csv_file_path = "../config/config.csv"
        try:
            with open(csv_file_path, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    map_name = row.get("map_name")
                    port_str = row.get("port")
                    if map_name not in self.map_names:
                        print(f"{map_name} is not a valid devices name.")
                        continue
                    try:
                        port = int(port_str)
                    except ValueError:
                        print(f"Invalid port number {port}. Please enter a valid integer >1000 for the port number.")
                        continue
                    server_identity = f"{map_name}_{self.i}"
                    self.device[server_identity] = port
                    map_obj = Map.objects.filter(name=map_name).first()
                    if map_obj:
                        fields = Field.objects.filter(map=map_obj)
                        self.field_dict[server_identity] = {f.field_address: f.ahe_name for f in fields}
                        self.get_field_dict[server_identity] = {f.ahe_name: f for f in fields}
                        data_block_size = max(self.field_dict[server_identity].keys()) + 1
                        self.set_context(server_identity, data_block_size)
                        self.set_all_initial_values_to_0(map_obj, server_identity)
                        self.maps[server_identity] = map_name
                        self.set_initial_config(map_name, server_identity)
                        thread = threading.Thread(target=run_slave,
                                                  args=(self.server_context[server_identity], port, map_name,))
                        thread.start()
                        self.threads.append(thread)
                    else:
                        print(f"Error: Map {map_name} not found in the database.")
                    self.i += 1
        except FileNotFoundError:
            print("Config file not found.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")

    def do_exit(self, _):
        print("Exiting code ...")
        return True

    def do_data(self, arg):
        if len(arg) == 0:
            print(self.data)
        else:
            print(self.data[arg])

    def do_map(self, _):
        print(self.map_names)

    def emptyline(self):
        pass


if __name__ == "__main__":
    modbus_cmd = ModbusSlaveCmd()
    modbus_cmd.cmdloop()

