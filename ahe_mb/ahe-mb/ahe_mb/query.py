import time
from collections import namedtuple
import ahe_log
import ahe_mb
from ahe_mb.variable import ModbusVar
from ahe_mb.connection import connect_modbus


Variable = namedtuple('Variable', ['name', 'var', 'address'])

def connect_device(device):
    if type(device) != ahe_mb.models.SiteDevice:
        raise TypeError("device should be of type ahe_mb.models.Device")
    return connect_modbus(device.ip_address, device.port)

class ModbusQuery():
    def __init__(self, device: ahe_mb.models.SiteDevice, address_range, device_map: ahe_mb.models.DeviceMap, block) -> None:
        self.block = block
        self.logging = ahe_log.get_logger("ModbusQuery")
        self.device_map = device_map
        self.device = device
        self.reg_type = self.device_map.map_reg
        self.address_range = address_range
        self.connection = connect_device(self.device)
        self.create_vars()

    def create_vars(self):
        self.address_to_variable = dict()
        self.name_to_variable = dict()
        print("map", self.device_map, self.device)
        device_start_address = 0

        device_start_address = self.device_map.start_address

        fields = self.device_map.map.detail.all()
        for field in fields:
            field_address = device_start_address + field.field_address
            if field_address < self.address_range[0] or field_address > self.address_range[1]:
                continue
            var = ModbusVar(field)
            name = f"{self.device.name}_{var.modbus_field.ahe_name}"
            v = Variable(name, var, field_address)
            self.address_to_variable[field_address] = v
            self.name_to_variable[name] = v
        self.name_to_address = {
            self.name_to_variable[i].name: self.name_to_variable[i].address for i in self.name_to_variable}

    def read(self):
        registers = self.connection.read(
            self.device.unit, self.reg_type, *self.address_range)
        if not registers:
            return None
        return self.assign_registers_to_variables(registers)

    def assign_registers_to_variables(self, registers):
        data = {"epoch": time.time()}
        for address in self.address_to_variable:
            var = self.address_to_variable[address].var
            name = self.address_to_variable[address].name
            # print("split ", registers, address, address + var.size)
            var.set_registers(
                registers[address - self.address_range[0]:address - self.address_range[0] + var.size])
            data[name] = var.value
        self.logging.debug(
            f"{time.time()}|MB$|{self.device.ip_address}:{self.device.port}#{self.device.unit}-{self.reg_type}@{self.address_range[0]}|var map|{self.name_to_address}")
        self.logging.debug(
            f"{time.time()}|MB$|{self.device.ip_address}:{self.device.port}#{self.device.unit}-{self.reg_type}@{self.address_range[0]}|data dict|{data}")
        return data

    def write(self, data):
        write_data = self.assign_values_to_variables(data)
        print("write_data", write_data)
        if not write_data:
            return
        write_buffers = self.data_to_buffers(write_data)
        print("write_buffers", write_buffers)
        for address in write_buffers:
            print("## writing ##", address, write_buffers[address] )
            status = self.connection.write(
                unit=self.device.unit, reg=self.reg_type, start_address=address, data=write_buffers[address],
                block=self.block)
            if status:
                return status
        return

    def data_to_buffers(self, write_data):
        buffers = {}
        data = []
        start_address = min(write_data.keys())
        end_address = max(write_data.keys())
        data_address = 0
        filling_buffer = True
        while start_address <= end_address:
            print("buffers", start_address, buffers)
            if filling_buffer:
                if start_address + data_address in write_data:
                    data.append(write_data[start_address + data_address])
                    data_address += 1
                else:
                    buffers[start_address] = data
                    data = []
                    filling_buffer = False
                    start_address = start_address + data_address + 1
                    data_address = 0
            else:
                if start_address in write_data:
                    filling_buffer = True
                else:
                    start_address += 1
        return buffers

    def assign_values_to_variables(self, data):
        if "command" in data:
            data_to_write = data["command"]
        else:
            data_to_write = data
        write_data = dict()
        for name in data_to_write:
            if name in self.name_to_variable:
                var = self.name_to_variable[name].var
                address = self.name_to_variable[name].address
                var.set_value(data_to_write[name])

                for x in range(len(var.registers)):
                    write_data[address + x] = var.registers[x]
        return write_data

