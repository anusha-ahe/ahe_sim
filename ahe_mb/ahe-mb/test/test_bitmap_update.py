import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import BitMapUpdate
from ahe_mb.models import BitMap
import unittest

bit_map_data = {"name": "bm1", "detail": [
    {"ahe_name": "a", "start_bit": 0, "end_bit": 0}]}


class TestBitMapUpdate(TestCase):

    def test_should_create_bitmap(self):
        smu = BitMapUpdate()
        bitmap = smu.upsert(bit_map_data)
        print("bitmap", bitmap.detail.all())
        self.assertEqual(bitmap.name, "bm1")
        self.assertEqual(bitmap.version, 1)
        self.assertGreaterEqual(len(bitmap.detail.all()), 1)

    def test_should_update_bitmap(self):
        smu = BitMapUpdate()
        bitmap = smu.upsert(bit_map_data)
        print("generated bitmap", bitmap)
        new_bit_map_data = copy.deepcopy(bit_map_data)
        new_bit_map_data["detail"][0]["end_bit"] = 2
        new_bit_map_data["id"] = bitmap.id
        print("--calling update")
        new_bitmap = smu.upsert(new_bit_map_data)
        print("--nn", bitmap)
        new_bits = new_bitmap.detail.all()
        self.assertEqual(new_bits[0].end_bit, 2)


