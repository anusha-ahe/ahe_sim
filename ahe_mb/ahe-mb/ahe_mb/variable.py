import math
import time
import ahe_log
from ahe_mb.models import Field 
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder


class ModbusVar:
    def __init__(self, modbus_field):
        self.logging = ahe_log.get_logger()
        if type(modbus_field) != Field:
            raise TypeError("var should be of type ahe_mb.models.Field")
        self.modbus_field = modbus_field
        self.compute_size()

    def compute_size(self):
        if self.modbus_field.field_format in ['uint16', 'boolean', 'coil', 'bitmap']:
            self.type = 'uint16'
            self.size = 1
        elif self.modbus_field.field_format in ["sint16", "int16"]:
            self.type = 'sint16'
            self.size = 1
        elif self.modbus_field.field_format in ["uint32"]:
            self.type = 'uint32'
            self.size = 2
        elif self.modbus_field.field_format in ["int32", "sint32"]:
            self.type = 'sint32'
            self.size = 2
        elif self.modbus_field.field_format in ["float32"]:
            self.type = 'float32'
            self.size = 2
        elif self.modbus_field.field_format.startswith("wstring"):
            self.type = "string"
            self.size = int(self.modbus_field.field_format[7:])
        elif self.modbus_field.field_format.startswith("warray"):
            self.type = "sint16"
            self.size = int(self.modbus_field.field_format[6:])
        else:
            raise KeyError(f"Unknown format {self.modbus_field.field_format}")

    def _create_builder(self):
        if self.modbus_field.field_encoding in ['', 'Big-endian']:
            return BinaryPayloadBuilder(
                byteorder=Endian.BIG, wordorder=Endian.BIG)
        elif self.modbus_field.field_encoding == 'Little-endian byte swap':
            return BinaryPayloadBuilder(
                byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        elif self.modbus_field.field_encoding == 'Little-endian':
            return BinaryPayloadBuilder(
                byteorder=Endian.LITTLE, wordorder=Endian.LITTLE)
        elif self.modbus_field.field_encoding == 'Big-endian byte swap':
            return BinaryPayloadBuilder(
                byteorder=Endian.LITTLE, wordorder=Endian.BIG)
        else:
            raise KeyError

    def _set_reg_for_value(self):
        builder = self._create_builder()
        self.logging.debug(
            f'Updating {self.modbus_field.ahe_name} to {self.value}')
        raw_value = (float(self.value) - self.modbus_field.field_offset) / \
            self.modbus_field.field_scale
        if self.type == "uint32":
            builder.add_32bit_uint(int(raw_value))
        elif self.type == "sint32":
            builder.add_32bit_int(int(raw_value))
        elif self.type == "float32":
            builder.add_32bit_float(raw_value)
        elif self.type == "uint16":
            builder.add_16bit_uint(int(raw_value))
        elif self.type == "sint16":
            builder.add_16bit_int(int(raw_value))
        else:
            self.logging.error(
                f"Unknown format: {self.format} for {self.modbus_field}")
            raise ValueError
        self.registers = builder.to_registers()
        self.logging.debug(f"Updated register {self.registers}")

    def clamp_value(self, value):
        if self.type == "uint32":
            value = max(0, min(value, 0xFFFFFFFF))
        elif self.type == "sint32":
            value = max(-0x80000000, min(value, 0x7FFFFFFF))
        elif self.type == "uint16":
            value = max(0, min(value, 0xFFFF))
        elif self.type == "sint16":
            value = max(-0x8000, min(value, 0x7FFF))
        return value

    def set_value(self, value):
        self.value = self.clamp_value(value)
        self._set_reg_for_value()

    def set_registers(self, registers):
        self.registers = registers[:]
        self._set_value_for_registers()
        self._set_bitmap_values()

    def _create_decoder(self):
        if self.modbus_field.field_encoding in [None, '', 'BB', 'ABCD', 'Big-endian']:
            return BinaryPayloadDecoder.fromRegisters(
                self.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
        elif self.modbus_field.field_encoding in ['BL', 'CDAB', 'Little-endian byte swap']:
            return BinaryPayloadDecoder.fromRegisters(
                self.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        elif self.modbus_field.field_encoding in ['LL', 'DCBA', 'Little-endian']:
            return BinaryPayloadDecoder.fromRegisters(
                self.registers, byteorder=Endian.LITTLE, wordorder=Endian.LITTLE)
        elif self.modbus_field.field_encoding in ['LB', 'BADC', 'Big-endian byte swap']:
            return BinaryPayloadDecoder.fromRegisters(
                self.registers, byteorder=Endian.LITTLE, wordorder=Endian.BIG)
        else:
            raise KeyError

    def _set_value_for_registers(self):
        decoder = self._create_decoder()
        if self.type == "uint32":
            decoded_value = decoder.decode_32bit_uint()
        elif self.type == "sint32":
            decoded_value = decoder.decode_32bit_int()
        elif self.type == "uint16":
            decoded_value = decoder.decode_16bit_uint()
        elif self.type == "float32":
            decoded_value = decoder.decode_32bit_float()
        elif self.type == "sint16":
            decoded_value = decoder.decode_16bit_int()
        else:
            self.logging.error(
                f"Unknown format: {self.format} for {self.modbus_field}")
            raise ValueError
        if self.modbus_field.field_scale == 0:
            scale = 1
        else:
            scale = self.modbus_field.field_scale
        value = decoded_value * scale + int(self.modbus_field.field_offset)
        if math.isnan(value):
            self.value = None
            self.logging.warning(
                f"{time.time()}|value is nan for {self.modbus_field.ahe_name}")
        elif self.modbus_field.max_value is not None and value > self.modbus_field.max_value:
            self.value = None
            self.logging.warning(
                f"{time.time()}|value beyond max for {self.modbus_field.ahe_name}")
        else:
            self.value = value
        if self.type in ["uint16", "sint16", "uint32",
                         "sint32"] and self.modbus_field.field_scale >= 1 and self.value is not None:
            self.value = int(self.value)

    def _slice_by_bits(self, var, start_bit, end_bit):
        comparison_map = 0
        for x in range(start_bit, end_bit):
            comparison_map += 1 << x
        print(f"{comparison_map:#04x}, {var:#04x}")
        return (var & comparison_map) >> start_bit

    def _set_bitmap_values(self):
        if not self.modbus_field.bit_map:
            return
        for bitmap_value in self.modbus_field.bit_map.bit_values.all():
            var_name = f'{self.modbus_field.ahe_name}_{bitmap_value.ahe_name}'
            self.values[var_name] = self._slice_by_bits(
                self.value, bitmap_value.start_bit, bitmap_value.end_bit)
            self.logging.debug(
                f"bitmap set {var_name} to {self.values[var_name]}")
