import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_common.updates import update_parameters
from ahe_mb.update import MapUpdate, DeviceMapUpdate, create_modbus_map, create_device_map, REF_DEVICE_TYPE, REF_MAP_DATA
from ahe_mb.models import Map
import unittest


class TestDeviceMapUpdate(TestCase):

    def test_should_create_device_map(self):
        dev = create_device_map()
        self.assertEqual(dev.name, REF_DEVICE_TYPE["name"])
        self.assertEqual(dev.version, 1)
        print("device", dev)
        print("all maps", dev.detail.all())
        self.assertGreaterEqual(len(dev.detail.all()), 1)
        map_names = [d.map.name for d in dev.detail.all()]
        self.assertIn(REF_MAP_DATA["name"], map_names)

    def test_should_create_device_map_with_params(self):
        map1 = create_modbus_map(name="map1")
        map2 = create_modbus_map(name="map2")
        detail = [{"map": map1.name}, {"map": map2.name}]
        dev = create_device_map(name="TestInv", detail=detail)
        self.assertEqual(dev.name, "TestInv")
        self.assertEqual(dev.version, 1)
        print("device", dev)
        print("all maps", dev.detail.all())
        self.assertGreaterEqual(len(dev.detail.all()), 1)
        map_names = [d.map.name for d in dev.detail.all()]
        self.assertIn("map1", map_names)
        self.assertIn("map2", map_names)

    def test_should_update_device_map(self):
        dev = create_device_map()
        dtu = DeviceMapUpdate()
        new_device_data = dtu.get(dev.id)
        new_device_data["detail"][0]["start_address"] = 2
        new_dev = dtu.upsert(new_device_data)
        new_fields = new_dev.detail.all()
        self.assertEqual(new_fields[0].start_address, 2)
        self.assertEqual(dev.version, 1)
        self.assertEqual(new_dev.version, 2)

