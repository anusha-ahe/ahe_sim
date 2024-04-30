import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import BitMapUpdate
from ahe_mb.models import BitMap
import unittest

bit_map_data = {"name": "bm1", "detail": [
    {"ahe_name": "a", "start_bit": 0, "end_bit": 0}]}


class TestBitMapAPI(TestCase):

    def test_should_receive_bitmap_list(self):
        client = Client()
        smu = BitMapUpdate()
        smu.upsert(bit_map_data)
        response = client.get(
            reverse('ahe_mb:bitmap-list'))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        names = [x["name"] for x in data_recv]
        self.assertIn("bm1", names)

    def test_should_receive_bitmap_detail(self):
        client = Client()
        smu = BitMapUpdate()
        bitmap = smu.upsert(bit_map_data)
        response = client.get(
            reverse('ahe_mb:bitmap-detail', kwargs={"name": bitmap.name}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "bm1")
        self.assertEqual(data_recv["version"], 1)

    def test_should_update_bitmap(self):
        client = Client()
        smu = BitMapUpdate()
        bitmap = smu.upsert(bit_map_data)
        data = smu.get(bitmap.id)
        print(data)
        data["detail"][0]["end_bit"] = 1
        response = client.put(
            reverse('ahe_mb:bitmap-detail', kwargs={"name": bitmap.name}), json.dumps(data), content_type='application/json')
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "bm1")
        self.assertEqual(data_recv["version"], 2)
        self.assertEqual(data_recv["detail"][0]["end_bit"], 1)
