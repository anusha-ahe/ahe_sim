from django.test import TestCase
from parameterized import parameterized
import ahe_mb
from ahe_mb.loader import ModbusLoader, BitMapLoader
from ahe_sys.common.loader import ERR_MISSING_IN_HEADER, MISSING_COLUMN_DATA, INVALID_VALUE, ALREADY_USED
import unittest


class TestLoader(TestCase):
    def setUp(self):
        # TODO change get_or_create to update
        ahe_mb.models.BitMap.objects.get_or_create(name="bm1")

    def _modbus_invalid_data(self, data, error):
        mbl = ModbusLoader()
        mbl.load_csv(data)
        print("Errors", mbl.err)
        self.assertIn(error, mbl.err)

    MODBUS_MISSING = [
        # ([{}], f"modbus_map {ERR_MISSING_IN_HEADER}"),
        ([{}], f"ahe_name {ERR_MISSING_IN_HEADER}"),
        ([{}], f"modbus_map {ERR_MISSING_IN_HEADER}"),
        ([{}], f"field_address {ERR_MISSING_IN_HEADER}"),
        ([{}], f"field_format {ERR_MISSING_IN_HEADER}"),
        ([{"ahe_name": "", "map_reg": "", "field_address": "", "field_format": ""}],
         f"modbus_map {ERR_MISSING_IN_HEADER}"),
        # ([{"ahe_name": "",  "field_address": "", "field_format": ""}],
        #  f"map_reg {ERR_MISSING_IN_HEADER}"),
        ([{"ahe_name": "", "map_reg": "", "field_address": ""}],
         f"field_format {ERR_MISSING_IN_HEADER}"),
        ([{"ahe_name": "", "map_reg": "", "field_format": ""}],
         f"field_address {ERR_MISSING_IN_HEADER}"),
    ]

    @parameterized.expand(MODBUS_MISSING)
    def test_modbus_missing_data(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_NAMES = [
        ([{"modbus_map": "t_inv", "ahe_name": "2", "map_reg": "1", "field_address": "0", "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"2 {INVALID_VALUE} ahe_name"),
        ([{"modbus_map": "t_inv", "ahe_name": "_", "map_reg": "1", "field_address": "0", "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"_ {INVALID_VALUE} ahe_name"),
        ([{"modbus_map": "t_inv", "ahe_name": "2b", "map_reg": "1", "field_address": "0", "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"2b {INVALID_VALUE} ahe_name"),
    ]

    @parameterized.expand(MODBUS_INVALID_NAMES)
    def test_modbus_invalid_map_name(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_REG = [
        ([{"modbus_map": "t_inv", "ahe_name": "b", "map_reg": "xxx", "field_address": "0", "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"xxx {INVALID_VALUE} map_reg"),
    ]

    @parameterized.expand(MODBUS_INVALID_REG)
    def test_modbus_invalid_reg(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_MAX_READ = [
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "0", "field_format": "x", "field_scale": 0, "field_offset": 0, "map_max_read": "z"}],
         f"z {INVALID_VALUE} map_max_read"),
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "0", "field_format": "x", "field_scale": 0, "field_offset": 0, "map_max_read": "1"}],
         f"1 {INVALID_VALUE} map_max_read"),
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "0", "field_format": "x", "field_scale": 0, "field_offset": 0, "map_max_read": "121"}],
         f"121 {INVALID_VALUE} map_max_read"),
    ]

    @parameterized.expand(MODBUS_INVALID_MAX_READ)
    def test_modbus_invalid_max_read(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_READ_SPACES = [
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "0", "field_format": "x", "field_scale": 0, "field_offset": 0, "read_spaces": "2"}],
         f"2 {INVALID_VALUE} read_spaces"),
    ]

    @parameterized.expand(MODBUS_INVALID_READ_SPACES)
    def test_modbus_invalid_read_space(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_FIELD_ADDRESS = [
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "u",
           "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"u {INVALID_VALUE} field_address"),
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "-1",
           "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"-1 {INVALID_VALUE} field_address"),
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "100000",
           "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"100000 {INVALID_VALUE} field_address"),
    ]

    @parameterized.expand(MODBUS_INVALID_FIELD_ADDRESS)
    def test_modbus_invalid_field_address(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_FIELD_ENCODING = [
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "1",
           "field_scale": 0, "field_offset": 0, "field_format": "x", "field_encoding": "f"}],
         f"f {INVALID_VALUE} field_encoding"),
    ]

    @parameterized.expand(MODBUS_INVALID_FIELD_ENCODING)
    def test_modbus_invalid_field_encoding(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_FIELD_FORMAT = [
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "1",
           "field_scale": 0, "field_offset": 0, "field_format": "x"}],
         f"x {INVALID_VALUE} field_format"),
    ]

    @parameterized.expand(MODBUS_INVALID_FIELD_FORMAT)
    def test_modbus_invalid_field_format(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_FIELD_SCALE = [
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "1",
            "field_format": "x", "field_offset": 0, "field_scale": 0}],
         f"0.0 {INVALID_VALUE} field_scale"),
    ]

    @parameterized.expand(MODBUS_INVALID_FIELD_SCALE)
    def test_modbus_invalid_field_scale(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_AHE_NAME = [
        ([{"modbus_map": "t_inv", "ahe_name": "", "map_reg": "Coil", "field_address": "100000",
           "field_format": "x", "field_scale": 0, "field_offset": 0, "field_encoding": "f"}],
            f" {INVALID_VALUE} ahe_name as bit_map is None")
    ]

    @parameterized.expand(MODBUS_INVALID_AHE_NAME)
    def test_modbus_invalid_ahe_name(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_BITMAP_SCALE = [
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "field_address": "1", "field_format": "uint16",
           "ahe_name": "a1", "field_scale": "2", "field_offset": 0, "bit_map": "bm1"}],
         f"2.0 {INVALID_VALUE} field_scale as bit_map is Not None"),
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "field_address": "1", "field_format": "float32",
           "ahe_name": "a1", "field_offset": 0, "field_scale": "2"}],
         f"2.0 {INVALID_VALUE} field_scale as field_format is float32"),
    ]

    @parameterized.expand(MODBUS_INVALID_BITMAP_SCALE)
    def test_modbus_invalid_bitmap_scale(self, data, error):
        self._modbus_invalid_data(data, error)

    MODBUS_INVALID_OFFSET = [
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "field_address": "1", "field_format": "float32",
           "ahe_name": "a1", "field_scale": "1", "field_offset": "1"}],
         f"1.0 {INVALID_VALUE} field_offset as field_format is float32"),]

    @parameterized.expand(MODBUS_INVALID_OFFSET)
    def test_modbus_invalid_offset(self, data, error):
        self._modbus_invalid_data(data, error)

    def _modbus_valid_data(self, data):
        bml = ModbusLoader()
        bml.load_csv(data, True)
        print(bml.err)
        self.assertEqual(0, len(bml.err))

    VALID_MODBUS_REG = [
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
         "field_address": "0", "field_scale": "2", "field_offset": 0, "field_format": "uint16"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Discrete Input",
           "field_address": "0", "field_scale": "2", "field_offset": 0, "field_format": "uint16"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Input Register",
           "field_address": "0", "field_scale": "2", "field_offset": 0, "field_format": "uint16"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Holding Register",
           "field_address": "0", "field_scale": "2", "field_offset": 0, "field_format": "uint16"}],),
    ]

    @parameterized.expand(VALID_MODBUS_REG)
    def test_modbus_valid_reg(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_MAX_READ = [
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
         "field_address": "0", "field_format": "uint16", "field_scale": "2", "field_offset": 0, "map_max_read": 2}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
         "field_address": "0", "field_format": "uint16", "field_scale": "2", "field_offset": 0, "map_max_read": 120}],),
    ]

    @parameterized.expand(VALID_MODBUS_MAX_READ)
    def test_modbus_valid_max_read(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_READ_COUNT = [
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
         "field_address": "0", "field_format": "uint16", "field_scale": "2", "field_offset": 0, "read_spaces": "False"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
         "field_address": "0", "field_format": "uint16", "field_scale": "2", "field_offset": 0, "read_spaces": "True"}],),
    ]

    @parameterized.expand(VALID_MODBUS_READ_COUNT)
    def test_modbus_valid_read_count(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_ENCODING = [
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil", "field_address": "0",
         "field_format": "uint16", "field_scale": "2", "field_offset": 0, "field_encoding": 'Big-endian'}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil", "field_address": "0",
         "field_format": "uint16", "field_scale": "2", "field_offset": 0, "field_encoding": 'Little-endian'}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil", "field_address": "0",
         "field_format": "uint16", "field_scale": "2", "field_offset": 0, "field_encoding": 'Big-endian byte swap'}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil", "field_address": "0",
         "field_format": "uint16", "field_scale": "2", "field_offset": 0, "field_encoding": 'Little-endian byte swap'}],),
    ]

    @parameterized.expand(VALID_MODBUS_ENCODING)
    def test_modbus_valid_encoding(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_FIELD_FORMAT = [
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "bitmap"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "boolean"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "string"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "array"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "sint16"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "uint32"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "sint32"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "float32"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_scale": "1", "field_offset": 0, "field_format": "Uint16"}],),
    ]

    @parameterized.expand(VALID_MODBUS_FIELD_FORMAT)
    def test_modbus_valid_field_format(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_FIELD_SCALE = [
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_format": "Uint16", "field_offset": 0, "field_scale": "1"}],),
        ([{"modbus_map": "t_inv", "ahe_name": "n1", "map_reg": "Coil",
           "field_address": "0", "field_format": "Uint16", "field_offset": 0, "field_scale": "0.1"}],),
    ]

    @parameterized.expand(VALID_MODBUS_FIELD_SCALE)
    def test_modbus_valid_field_scale(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_AHE_NAME = [
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "field_address": "1",
         "field_format": "uint16", "field_scale": "2", "field_offset": 0, "ahe_name": "no_bit_map"}],),
    ]

    @parameterized.expand(VALID_MODBUS_AHE_NAME)
    def test_modbus_valid_ahe_name(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_BITMAP_AHE_NAME = [
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "ahe_name": "", 
           "field_address": "1", "field_scale": "1", "field_offset": 0, "bit_map": "bm1",
         "field_format": "uint16", "ahe_name": ""}],),
        # ([{"modbus_map": "t_inv", "map_reg": "Coil",
        #    "field_address": "1", "field_scale": "1", "field_offset": 0, "bit_map": "bm1",
        #  "field_format": "uint16"}],),
    ]

    @parameterized.expand(VALID_MODBUS_BITMAP_AHE_NAME)
    def test_modbus_valid_bitmap_ahe_name(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_UNIT_FIELD_SCALE = [
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "field_address": "1", "bit_map": "bm1", "ahe_name": "", 
            "field_format": "uint16", "field_offset": 0, "field_scale": "1"}],),
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "field_address": "1", "ahe_name": "f1",
            "field_format": "float32", "field_offset": 0, "field_scale": "1"}],),
    ]

    @parameterized.expand(VALID_MODBUS_UNIT_FIELD_SCALE)
    def test_modbus_valid_fixed_field_scale(self, data):
        self._modbus_valid_data(data)

    VALID_MODBUS_ZERO_OFFSET = [
        ([{"modbus_map": "t_inv", "map_reg": "Coil", "field_address": "1", "ahe_name": "f1",
            "field_format": "float32", "field_scale": "1", "field_offset": "0"}],),
    ]

    @parameterized.expand(VALID_MODBUS_ZERO_OFFSET)
    def test_modbus_valid_zero_offset(self, data):
        self._modbus_valid_data(data)
