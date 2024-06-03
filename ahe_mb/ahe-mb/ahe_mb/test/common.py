from django.test import TestCase
from random import randint
from ahe_mb.slave import run_server
from ahe_sys.update import create_site
from ahe_mb.test.prepare import create_test_devices
from ahe_mb.update import create_modbus_map

class TestModbus(TestCase):

    def setUp(self):
        self.site = create_site(999, "site 999")
        self.modbus = create_modbus_map(name="mb_t1")
        self.modbus_coil = create_modbus_map(name='mb_coil', map_reg="Coil")
        self.device1 = create_test_devices()
        # self.device2 = create_test_device(
        #     'mb_d2', self.modbus, self.site)
        # self.device_coil = create_test_device_with_coil(
        #     'mb_coil', self.modbus_coil, self.site)
        # self.device_coil1 = create_test_device_with_coil(
        #     'mb_coil1', self.modbus_coil, self.site)
        # self.device_invalid = create_test_device(
        #     'mb_d3', self.modbus, self.site, port=5021)
