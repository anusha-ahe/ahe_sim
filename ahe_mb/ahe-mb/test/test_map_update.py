import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import MapUpdate, BitMapUpdate
from ahe_mb.models import Map
from ahe_sys.update import DeviceTypeUpdate
import unittest

DEVICE_TYPE_DICT = {
    "name": "Test inv",
    "device_category": "inverter",
    "interface_type": "MODBUS"
}

map_data = {"name": "test_map1", "detail": [
    {"ahe_name": "a", "field_address": 0, "field_format": "uint16", "description": "b"}]}

bit_map_data = {"name": "bm1", "detail": [
    {"ahe_name": "a", "start_bit": 0, "end_bit": 0}]}


class TestMapUpdate(TestCase):

    def test_should_create_map(self):
        smu = MapUpdate()
        map_data_dict = copy.deepcopy(map_data)
        print("map_data_dict", map_data_dict)
        map_obj = smu.upsert(map_data_dict)
        print("bitmap", map_obj.detail.all())
        self.assertEqual(map_obj.name, "test_map1")
        self.assertEqual(map_obj.version, 1)
        self.assertGreaterEqual(len(map_obj.detail.all()), 1)

    def test_should_update_map(self):
        smu = MapUpdate()
        map_data_dict = copy.deepcopy(map_data)
        map_obj = smu.upsert(map_data_dict)
        print("generated bitmap", map_obj)
        new_map_data = copy.deepcopy(map_data_dict)
        new_map_data["detail"][0]["field_address"] = 2
        new_map = smu.upsert(new_map_data)
        print("--nn", map_obj)
        new_fields = new_map.detail.all()
        self.assertEqual(new_fields[0].field_address, 2)

    def test_should_update_map_bitmap_version(self):
        bmu = BitMapUpdate()
        bitmap = bmu.upsert(bit_map_data)
        smu = MapUpdate()
        map_data_dict = copy.deepcopy(map_data)
        map_data_dict["detail"][0]["bit_map"] = bitmap.name
        map_obj = smu.upsert(map_data_dict)
        print(map_obj, map_obj)
        new_bit_map_data = copy.deepcopy(bit_map_data)
        new_bit_map_data["detail"][0]["end_bit"] = 2
        new_bit_map_data["id"] = bitmap.name
        print("--calling update")
        new_bitmap = bmu.upsert(new_bit_map_data)
        new_map_obj = smu.upsert(map_data_dict)
        self.assertEqual(map_obj.version, 1)
        self.assertEqual(new_map_obj.version, 2)
        print(new_bitmap.version)
        print(new_map_obj.detail.all()[0].bit_map.version)
        self.assertEqual(new_bitmap.version, 2)
        self.assertEqual(new_map_obj.detail.all()[0].bit_map.version, 2)


