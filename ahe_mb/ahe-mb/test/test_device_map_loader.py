from django.test import TestCase
from parameterized import parameterized
import ahe_mb
from ahe_mb.loader import DeviceMapLoader
from ahe_mb.update import create_device_map
from ahe_sys.common.loader import ERR_MISSING_IN_HEADER, MISSING_COLUMN_DATA, INVALID_VALUE, ALREADY_USED
import unittest


class TestDevieMapLoader(TestCase):

    def _device_map_invalid_data(self, data, error):
        bml = DeviceMapLoader()
        bml.load_csv(data)
        print(bml.err)
        self.assertIn(error, bml.err)

    DEVICE_MAP_MISSIG_DATA = [
        ([{}], f"name {ERR_MISSING_IN_HEADER}"),
        ([{}], f"device_category {ERR_MISSING_IN_HEADER}"),
        ([{}], f"start_address {ERR_MISSING_IN_HEADER}"),
        ([{}], f"map {ERR_MISSING_IN_HEADER}"),
        ([{"name": "", "device_category": "", "start_address": "", "map": ""}],
         f"name {MISSING_COLUMN_DATA}"),
        ([{"name": "", "device_category": "", "start_address": "", "map": ""}],
         f"device_category {MISSING_COLUMN_DATA}"),
        ([{"name": "", "device_category": "", "start_address": "", "map": ""}],
         f"start_address {MISSING_COLUMN_DATA}"),
        ([{"name": "", "device_category": "", "start_address": "", "map": ""}],
         f"map {MISSING_COLUMN_DATA}"),
    ]

    @parameterized.expand(DEVICE_MAP_MISSIG_DATA)
    def test_device_map_missing_data(self, data, error):
        self._device_map_invalid_data(data, error)


    DEVICE_MAP_INVALID_DATA = [
        ([{"name": "D1", "device_category": "x", "start_address": 0, "map": "A"}],
         f"x {INVALID_VALUE} device_category"),

        ([{"name": "D1", "device_category": "inverter", "start_address": 0, "map": "A", "map_reg": "x"}],
         f"x {INVALID_VALUE} map_reg"),

        ([{"name": "D1", "device_category": "inverter", "start_address": 0, "map": "A", "map_max_read": 126}],
         f"126 {INVALID_VALUE} map_max_read"),
    ]

    @parameterized.expand(DEVICE_MAP_INVALID_DATA)
    def test_device_map_invalid_values(self, data, error):
        self._device_map_invalid_data(data, error)

    def _device_map_valid_data(self, data):
        print("Load device_map", data)
        create_device_map()
        bml = DeviceMapLoader()
        bml.load_csv(data, True)
        print(bml.err)
        self.assertEqual(0, len(bml.err))

    VALID_DEVICE_MAP = [
        ([{"name": "D1", "device_category": "inverter", "start_address": 0, "map": "test_map1"}],)
    ]

    @parameterized.expand(VALID_DEVICE_MAP)
    def test_device_map_valid_device_map(self, data):
        self._device_map_valid_data(data)

