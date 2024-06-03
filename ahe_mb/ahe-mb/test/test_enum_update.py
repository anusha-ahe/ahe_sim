import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import EnumUpdate
from ahe_mb.models import Enum
import unittest

enum_data = {"name": "enum_1", "detail": [
    {"ahe_name": "a", "value": 10}]}


class TestEnumUpdate(TestCase):

    def test_should_create_enum(self):
        smu = EnumUpdate()
        enum = smu.upsert(enum_data)
        print("enum", enum.detail.all())
        self.assertEqual(enum.name, "enum_1")
        self.assertEqual(enum.version, 1)
        self.assertGreaterEqual(len(enum.detail.all()), 1)

    def test_should_update_enum(self):
        smu = EnumUpdate()
        enum = smu.upsert(enum_data)
        print("generated enum", enum)
        new_enum_data = copy.deepcopy(enum_data)
        new_enum_data["detail"][0]["value"] = 20
        new_enum_data["id"] = enum.id
        print("--calling update")
        new_enum = smu.upsert(new_enum_data)
        print("--nn", enum)
        new_values = new_enum.detail.all()
        self.assertEqual(new_values[0].value, 20)


