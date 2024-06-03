from django.test import TestCase, Client
from django.test.client import encode_multipart, RequestFactory
from ahe_mb.update import create_modbus_map
from ahe_sys.update import create_site
from ahe_mb.models import Map, Field
import json
import os
import pytest
import unittest


class ModbusDeviceApiTest(TestCase):

    def setUp(self):
        self.site = create_site(881, "test")
        self.modbus = create_modbus_map("mb1")
        self.register = "Holding Register"

    @unittest.skip("Design changed in ahe_sys")
    def test_get_api_for_one_device(self):
        expected_res = [{"id": 18, "site": 881, "name": "mb_d1", "map": "mb_t1", "ip_address": "127.0.0.1", "port": 5020,
                         "unit": 1, "start_address": 1, "data_hold_period": 60}]
        field_data = [{'field_address': 0,
                       'ahe_name': 'v1',
                       "field_format": 'uint16'},
                      {'field_address': 1,
                       'ahe_name': 'v2',
                       "field_format": "uint32"}]
        modbus = create_modbus_map("mb_t1", field_data)
        device = create_test_device(
            'mb_d1', modbus, self.site, start_address=1)
        expected_res[0]["id"] = device.id
        view = ModbusDeviceView.as_view()
        factory = RequestFactory()
        req = factory.get('/ahe-mb/device')
        response = view(req, 881, device.id)
        print(expected_res)
        print(response.data)
        print(modbus.id)
        self.assertEqual(response.data[0]["id"], expected_res[0]["id"])
        self.assertEqual(response.data[0]["site"], expected_res[0]["site"])
        self.assertEqual(response.data[0]["map"], modbus.id)
        self.assertEqual(response.data[0]["name"], expected_res[0]["name"])
        self.assertEqual(response.data[0]["ip_address"],
                         expected_res[0]["ip_address"])
        self.assertEqual(response.data[0]["port"], expected_res[0]["port"])
        self.assertEqual(response.data[0]["unit"], expected_res[0]["unit"])

    @unittest.skip("Design changed in ahe_sys")
    def test_get_api_for_all_devices_for_site(self):
        expected_res = [
            {
                "id": 18,
                "site": 881,
                "name": "mb_d1",
                "map": "mb_t1",
                "ip_address": "127.0.0.1",
                "port": 5020,
                "unit": 1,
                "start_address": 1,
                "data_hold_period": 60
            },
            {
                "id": 18,
                "site": 881,
                "name": "mb_d12",
                "map": "mb_t1",
                "ip_address": "127.0.0.1",
                "port": 5020,
                "unit": 1,
                "start_address": 1,
                "data_hold_period": 60}
        ]
        field_data = [{'field_address': 0,
                       'name': 'v1',
                       "field_format": 'uint16'},
                      {'field_address': 1,
                       'name': 'v2',
                       "field_format": "unit32"}]
        modbus, _fields = create_modbus_map("mb_t1", field_data)
        # device_1 = create_test_device(
        #     'mb_d1', modbus, self.site, start_address=1)
        # device_2 = create_test_device(
        #     'mb_d12', modbus, self.site, start_address=1)
        # expected_res[0]["id"] = device_1.id
        # expected_res[1]["id"] = device_2.id
        # view = ModbusDeviceView.as_view()
        factory = RequestFactory()
        req = factory.get('/ahe-mb/device')
        # response = view(req, 881)
        # self.assertEqual(response.data, expected_res)


class ListOfFieldsApiTest(TestCase):

    def setUp(self):
        self.site = create_site(881, "test")

    @unittest.skip("Design changed in ahe_sys")
    def test_get_list_of_items(self):
        field_data = [{'field_address': 0,
                       'name': 'v1',
                       "field_format": 'uint16'},
                      {'field_address': 1,
                       'name': 'v2',
                       "field_format": "unit32"}]
        modbus = create_modbus_map("mb_t1", field_data)
        view = ModbusFieldListView.as_view()
        create_test_device(
            'mb_d1', modbus, self.site, start_address=1)
        factory = RequestFactory()
        req = factory.get('/ahe-mb/list-of-fields')
        response = view(req, "mb_d1")
        self.assertEqual(response.data, ["mb_d1_v1", "mb_d1_v2"])

    @unittest.skip("Design changed in ahe_sys")
    def test_should_return_empty_list_if_wrong_device_name_passed(self):
        field_data = [{'field_address': 0,
                       'name': 'v1',
                       "field_format": 'uint16'},
                      {'field_address': 1,
                       'name': 'v2',
                       "field_format": "unit32"}]
        modbus = create_modbus_map("mb_t1", field_data)
        view = ModbusFieldListView.as_view()
        create_test_device(
            'mb_d1', modbus, self.site, start_address=1)
        factory = RequestFactory()
        req = factory.get('/ahe-mb/list-of-fields')
        response = view(req, "mb_d2")
        self.assertEqual(response.data, [])

