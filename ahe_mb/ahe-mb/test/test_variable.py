from django.test import TestCase
from parameterized import parameterized
from ahe_sys.update import create_site_args
from ahe_mb.test.prepare import create_test_field
from ahe_mb.update import create_modbus_map
import ahe_mb
from ahe_mb.variable import ModbusVar
import pytest
import unittest


class TestVariables(TestCase):
    def setUp(self):
        self.site = create_site_args(id=999, name="site 999")
        self.modbus = create_modbus_map(name="mb_t1")

    def test_correct_setup(self):
        self.assertIsNotNone(self.modbus)
        # self.assertIsNotNone(self.fields)

    def test_modbus_var_should_need_field(self):
        with self.assertRaises(TypeError):
            ModbusVar("")

    @parameterized.expand([
        ["coil", "uint16", 1],
        ["boolean", "uint16", 1],
        ["bitmap", "uint16", 1],
        ["uint16", "uint16", 1],
        ["sint16", "sint16", 1],
        ["int16", "sint16", 1],
        ["uint32", "uint32", 2],
        ["sint32", "sint32", 2],
        ["int32", "sint32", 2],
        ["float32", "float32", 2],
        ["wstring10", "string", 10],
        ["warray8", "sint16", 8],
    ])
    def test_variable_size(self, field_format, field_type, field_size):
        params = {'field_format': field_format, "map": self.modbus}
        fld = create_test_field(**params)
        var1 = ModbusVar(fld)
        self.assertEqual(var1.size, field_size)
        self.assertEqual(var1.type, field_type)

    def test_variable_invalid_format(self):
        params = {'field_format': "xxxx", "map": self.modbus}
        fld = create_test_field(**params)
        with self.assertRaises(KeyError):
            ModbusVar(fld)

    LE_BS = 'Little-endian byte swap'
    BE_BS = 'Big-endian byte swap'
    VAR_ENCODING = [('Big-endian', 'uint32', 1, [0, 1]),
                    ('Big-endian', 'uint32', 0, [0, 0]),
                    ('Big-endian', 'uint32', 123, [0, 123]),
                    ('Big-endian', 'uint32', 0x10000 * 1, [1, 0]),
                    ('Big-endian', 'uint32', 0x10000 * 5, [5, 0]),
                    ('Big-endian', 'uint32', 0xFFFFFFFF, [0xFFFF, 0xFFFF]),
                    ('Big-endian', 'sint32', 1, [0, 1]),
                    ('Big-endian', 'sint32', 0, [0, 0]),
                    ('Big-endian', 'sint32', -2, [0xFFFF, 0xFFFE]),
                    ('Big-endian', 'sint32', 123, [0, 123]),
                    ('Big-endian', 'sint32', 0x10000 * 1, [1, 0]),
                    ('Big-endian', 'sint32', 0x10000 * 5, [5, 0]),
                    ('Big-endian', 'sint32', 0x7FFFFFFF, [0x7FFF, 0xFFFF]),
                    ('Big-endian', 'sint32', -0x80000000, [0x8000, 0]),
                    ('Big-endian', 'int32', 1, [0, 1]),
                    ('Big-endian', 'int32', -2, [0xFFFF, 0xFFFE]),
                    ('Big-endian', 'float32', 1, [0x3f80, 0]),
                    ('Big-endian', 'float32', 0, [0, 0]),
                    ('Big-endian', 'float32', 2, [0x4000, 0]),
                    ('Big-endian', 'float32', 0.5, [0x3f00, 0]),
                    ('Big-endian', 'float32', 1.00390625, [0x3f80, 0x8000]),
                    ('Big-endian', 'float32', -1.00390625, [0xbf80, 0x8000]),

                    ('', 'uint16', 0, [0]),
                    ('', 'uint16', 1, [1]),
                    ('', 'uint16', 123, [123]),
                    ('', 'uint16', 0xFFFF, [0xFFFF]),

                    ('', 'sint16', 0, [0]),
                    ('', 'sint16', 1, [1]),
                    ('', 'sint16', 0x7FFF, [0x7FFF]),
                    ('', 'sint16', -1, [0xFFFF]),
                    ('', 'sint16', -0x7FFF - 1, [0x8000]),
                    ('', 'int16', 0, [0]),
                    ('', 'int16', 1, [1]),
                    ('', 'int16', 0x7FFF, [0x7FFF]),
                    ('', 'int16', -1, [0xFFFF]),
                    ('', 'int16', -0x7FFF - 1, [0x8000]),

                    ('', 'coil', 1, [1]),
                    ('', 'boolean', 1, [1]),

                    (LE_BS, 'uint32', 1, [1, 0]),
                    (LE_BS, 'uint32', 0x10000 * 1, [0, 1]),
                    (LE_BS,
                     'sint32', -2, [0xFFFE, 0xFFFF]),
                    (LE_BS, 'sint32', 123, [123, 0]),

                    (LE_BS, 'float32', 2, [0, 0x4000]),


                    ('Little-endian', 'uint32', 1, [0x0100, 0]),
                    ('Little-endian', 'uint32', 0x100, [1, 0]),
                    ('Little-endian', 'uint32', 0x10000, [0, 0x0100]),
                    ('Little-endian', 'uint32', 0x1000000, [0, 1]),

                    (BE_BS, 'uint32', 1, [0, 0x0100]),
                    (BE_BS, 'uint32', 0x100, [0, 1]),
                    (BE_BS, 'uint32', 0x10000, [0x0100, 0]),
                    (BE_BS, 'uint32', 0x1000000, [1, 0]),
                    ]
    VAR_RANGE_ERROR = [('Big-endian', 'uint32', -1, [0, 0]),
                       ('Big-endian', 'uint32',
                        0xFFFFFFFF + 1, [0xFFFF, 0xFFFF]),
                       ('Big-endian', 'sint32',
                        0x7FFFFFFF + 1, [0x7FFF, 0xFFFF]),
                       ('Big-endian', 'sint32', -0x80000000 - 1, [0x8000, 0]),
                       ('', 'uint16', 0xFFFF + 1, [0xFFFF]),
                       ('', 'uint16', -1, [0]),
                       ('', 'sint16', 0x7FFF + 1, [0x7FFF]),
                       ('', 'sint16', -0x8000 - 1, [0x8000]),
                       ]

    @parameterized.expand(VAR_ENCODING + VAR_RANGE_ERROR)
    def test_encoding_value_to_register(self, field_encoding, field_format, value, registers):
        params = {'field_format': field_format,
                  "field_encoding": field_encoding,
                  "map": self.modbus}
        fld = create_test_field(**params)
        mb_v1 = ModbusVar(fld)
        mb_v1.set_value(value)
        print("Registers", mb_v1.registers, "value", mb_v1.value)
        assert mb_v1.registers == registers

    @parameterized.expand(VAR_ENCODING)
    def test_decoding_register_to_value(self, field_encoding, field_format, value, registers):
        params = {'field_format': field_format,
                  "field_encoding": field_encoding,
                  "map": self.modbus}
        fld = create_test_field(**params)
        mb_v1 = ModbusVar(fld)
        mb_v1.set_registers(registers)
        print("Registers", mb_v1.registers, "value", mb_v1.value)
        assert mb_v1.value == value

    def test_decoding_for_max_value(self):
        params = {'field_format': 'uint16',
                  "field_encoding": 'Big-endian',
                  "map": self.modbus,
                  "max_value": 0xFFFE}
        fld = create_test_field(**params)
        mb_v1 = ModbusVar(fld)
        mb_v1.set_registers([0xFFFF])
        print("Registers", mb_v1.registers, "value", mb_v1.value)
        assert mb_v1.value == None

    VAR_SCALE_OFFSET = [(100, 1, 0, [100]),
                        (100, 10, 0, [10]),
                        (100, 100, 0, [1]),
                        (.1, .1, 0, [1]),
                        (.1, .01, 0, [10]),
                        (100, 1, -1, [101]),
                        (100, 1, 1, [99]),
                        ]

    @parameterized.expand(VAR_SCALE_OFFSET)
    def test_scale_register_to_value(self, value, scale, offset, registers):
        params = {"map": self.modbus,
                  "field_scale": scale,
                  "field_offset": offset
                  }
        fld = create_test_field(**params)
        mb_v1 = ModbusVar(fld)
        mb_v1.set_value(value)
        print("Registers", mb_v1.registers, "value", mb_v1.value)
        assert mb_v1.registers == registers

    @parameterized.expand(VAR_SCALE_OFFSET)
    def test_scale_value_to_register(self, value, scale, offset, registers):
        params = {"map": self.modbus,
                  "field_scale": scale,
                  "field_offset": offset
                  }
        fld = create_test_field(**params)
        mb_v1 = ModbusVar(fld)
        mb_v1.set_registers(registers)
        print("Registers", mb_v1.registers, "value", mb_v1.value)
        assert mb_v1.value == value

    def test_should_raise_error_if_modbus_field_address_is_overlap(self):
        with pytest.raises(ValueError):
            field_data = [{'field_address': 1,
                           'ahe_name': 'v2',
                           "field_format": "unit32",
                           "field_size": 2},
                          {'field_address': 2,
                           'ahe_name': 'v3',
                           "field_format": "unit32"}]
            create_modbus_map(name="test_modbus", detail=field_data)

    TEST_BIT_DECODE = [
        (0xFF, 0, 1, 1),
        (0x01, 0, 1, 1),
        (0x00, 0, 1, 0),
        (0xFE, 0, 1, 0),
        (0xFF, 4, 5, 1),
        (0x10, 4, 5, 1),
        (0x00, 4, 5, 0),
        (0xEF, 4, 5, 0),
        (0x80, 7, 8, 1),
        (0x7F, 7, 8, 0),
        (0x00, 4, 6, 0),
        (0x10, 4, 6, 1),
        (0x20, 4, 6, 2),
        (0x30, 4, 6, 3),
        (0x00, 3, 6, 0),
        (0x08, 3, 6, 1),
        (0x10, 3, 6, 2),
        (0x18, 3, 6, 3),
        (0x20, 3, 6, 4),
        (0x28, 3, 6, 5),
        (0x30, 3, 6, 6),
        (0x38, 3, 6, 7),
    ]

    @parameterized.expand(TEST_BIT_DECODE)
    def test_bitmap_decode(self, var, start_bit, end_bit, value):
        params = {"map": self.modbus}
        fld = create_test_field(**params)
        var1 = ModbusVar(fld)
        result = var1._slice_by_bits(var, start_bit, end_bit)
        self.assertEqual(result, value)

    def test_bitmap_variable(self):
        registers = [0x0000]
        value = 0
        params = {"map": self.modbus}
        fld = create_test_field(**params)
        mb_v1 = ModbusVar(fld)
        mb_v1.set_registers(registers)
        print("Registers", mb_v1.registers, "value", mb_v1.value)
        assert mb_v1.value == value
