from ahe_mb.test.prepare import create_test_devices
from ahe_mb.update import create_modbus_map
from django.test import TestCase
from ahe_mb.models import Map, Field
import unittest

class TestPrepare(TestCase):

    def test_should_create_modbus_map(self):
        create_modbus_map(name="test_mb_map")
        map_objects = Map.objects.filter(name="test_mb_map")
        print("map_objects", map_objects)
        self.assertEqual(len(map_objects), 1)

    @unittest.skip("redesign")
    def test_should_create_modbus_device(self):
        device_conf = create_test_devices()
        print("device_conf", device_conf)
        print("devices", device_conf.devices.all())
        self.assertEqual(len(device_conf.devices.all()), 1)
