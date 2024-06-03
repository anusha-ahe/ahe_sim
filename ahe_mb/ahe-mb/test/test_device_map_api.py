import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import MapUpdate, DeviceMapUpdate, REF_DEVICE_TYPE, create_device_map
import unittest

map_data = {"name": "test_map1", "detail": [
    {"ahe_name": "a", "field_address": 0, "field_format": "uint16", "description": "b"}]}


class TestDeviceMapAPI(TestCase):

    def test_should_receive_device_list(self):
        client = Client()
        dev = create_device_map()
        response = client.get(
            reverse('ahe_mb:device-map-list'))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        names = [x["name"] for x in data_recv]
        self.assertIn("Test inv", names)

    def test_should_receive_device_detail(self):
        client = Client()
        dev = create_device_map()
        response = client.get(
            reverse('ahe_mb:device-map-detail', kwargs={"name": dev.name}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "Test inv")
        self.assertEqual(data_recv["version"], 1)

    def test_should_update_device_map(self):
        client = Client()
        dev = create_device_map()
        response = client.get(
            reverse('ahe_mb:device-map-detail', kwargs={"name": dev.name}))
        print("response is ", response.content)
        dtu = DeviceMapUpdate()
        data = dtu.get(dev.id)
        print("data", data)
        data["detail"][0]["start_address"] = 10
        response = client.put(
            reverse('ahe_mb:device-map-detail', kwargs={"name": dev.name}), json.dumps(data), content_type='application/json')
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "Test inv")
        self.assertEqual(data_recv["version"], 2)
        self.assertEqual(data_recv["detail"][0]["start_address"], 10)
