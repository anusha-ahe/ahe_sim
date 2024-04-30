import ahe_mb
from django.test import TestCase, Client
# from ahe_mb.test.prepare import create_test_device, create_test_modbus
from ahe_sys.update import create_site
import unittest


class TestCopyMbDevice(TestCase):

    @unittest.skip("Design changed in ahe_sys")
    def test_copy_mb_device(self):
        expected_res = {'modbus_devices': [
                        {'site': 882,
                         'name': 'mb_d1',
                         'map': 'mb_t1',
                         'ip_address': '127.0.0.1',
                         'port': 5020,
                         'unit': 1,
                         'start_address': 0,
                         'data_hold_period': 60}]
                        }
        site = create_site(881, "test")
        create_site(882, "test")
        create_test_modbus("mb1")
        field_data = [{'field_address': 0,
                       'name': 'v1',
                       "field_format": 'uint16'},
                      {'field_address': 1,
                       'name': 'v2',
                       "field_format": "unit32"}]
        modbus = create_test_modbus("mb_t1", field_data)
        create_test_device(
            'mb_d1', modbus, site, start_address=0)
        device_config = ahe_mb.copy_mb_devices(882, 881)
        # print(device_config)
        self.assertEqual(device_config, expected_res)
