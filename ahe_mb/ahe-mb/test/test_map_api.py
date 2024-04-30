import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import MapUpdate, BitMapUpdate, create_modbus_map
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


class TestMapAPI(TestCase):

    def test_should_receive_map_list(self):
        client = Client()
        smu = MapUpdate()
        map_data_dict = copy.deepcopy(map_data)
        smu.upsert(map_data_dict)
        response = client.get(
            reverse('ahe_mb:map-list'))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        names = [x["name"] for x in data_recv]
        self.assertIn("test_map1", names)

    def test_should_receive_map_detail(self):
        client = Client()
        smu = MapUpdate()
        map_data_dict = copy.deepcopy(map_data)
        map_obj = smu.upsert(map_data_dict)
        response = client.get(
            reverse('ahe_mb:map-detail', kwargs={"name": map_obj.name}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "test_map1")
        self.assertEqual(data_recv["version"], 1)

    def test_should_update_map_field(self):
        client = Client()
        map_obj = create_modbus_map(**map_data)
        data = copy.deepcopy(map_data)
        data["detail"][0]["field_address"] = 1
        response = client.put(
            reverse('ahe_mb:map-detail', kwargs={"name": map_obj.name}), json.dumps(data), content_type='application/json')
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "test_map1")
        self.assertEqual(data_recv["version"], 2)
        self.assertEqual(data_recv["detail"][0]["field_address"], 1)

    def test_should_double_update_map_field(self):
        client = Client()
        map_obj1 = create_modbus_map(**map_data)
        print("map_obj1 version", map_obj1.version)
        map_obj = create_modbus_map(**map_data)
        print("map_obj version", map_obj.version)
        data = copy.deepcopy(map_data)
        data["detail"][0]["field_address"] = 1
        response = client.put(
            reverse('ahe_mb:map-detail', kwargs={"name": map_obj.name}), json.dumps(data), content_type='application/json')
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "test_map1")
        self.assertEqual(data_recv["version"], 3)
        self.assertEqual(data_recv["detail"][0]["field_address"], 1)
