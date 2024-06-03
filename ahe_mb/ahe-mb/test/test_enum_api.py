import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import EnumUpdate
from ahe_mb.models import Enum
import unittest

enum_data = {"name": "enum_1", "detail": [
    {"ahe_name": "a", "value": 10}]}


class TestEnumAPI(TestCase):

    def test_should_receive_enum_list(self):
        client = Client()
        smu = EnumUpdate()
        smu.upsert(enum_data)
        response = client.get(
            reverse('ahe_mb:enum-list'))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        # self.assertEqual(data_recv[0]["name"], "enum_1")

    def test_should_receive_enum_detail(self):
        client = Client()
        smu = EnumUpdate()
        enum = smu.upsert(enum_data)
        response = client.get(
            reverse('ahe_mb:enum-detail', kwargs={"name": enum.name}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "enum_1")
        self.assertEqual(data_recv["version"], 1)

    def test_should_update_enum(self):
        client = Client()
        smu = EnumUpdate()
        enum = smu.upsert(enum_data)
        data = smu.get(enum.id)
        print(data)
        data["detail"][0]["value"] = 1
        response = client.put(
            reverse('ahe_mb:enum-detail', kwargs={"name": enum.name}), json.dumps(data), content_type='application/json')
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "enum_1")
        self.assertEqual(data_recv["version"], 2)
        self.assertEqual(data_recv["detail"][0]["value"], 1)
