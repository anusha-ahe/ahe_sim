import copy
import json
from django.test import Client, TestCase
from django.urls import reverse
from ahe_mb.update import SiteDeviceConfUpdate
from ahe_sys.update import SiteUpdate, DeviceTypeUpdate, REF_DEVICE_TYPE 
from ahe_mb.models import BitMap
import unittest

DEVICE_1 = { "name": "test_device_1", "ip_address": 0, "port": 0, "unit": 0}


class TestDeviceAPI(TestCase):

    @unittest.skip("redesign")
    def test_should_receive_device_list(self):
        client = Client()
        sup = SiteUpdate()
        dtu = DeviceTypeUpdate()
        sdu = SiteDeviceConfUpdate()
        sup.upsert({"id": 998, "name": "abc"})
        dev_type = dtu.upsert(REF_DEVICE_TYPE)
        dev_1 = copy.copy(DEVICE_1)
        dev_1["device_type"] = dev_type.id
        device_cong_data = {"site": 998, "devices": [dev_1]}
        print("Device conf", device_cong_data, dev_type)
        device_conf_obj = sdu.upsert(device_cong_data)

        response = client.get(
            reverse('ahe_mb:devices-list'))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        print(data_recv)
        self.assertIsInstance(data_recv, list)
        self.assertGreaterEqual(len(data_recv), 1)
        found_hr = False
        print("data_recv", data_recv)
        for x in data_recv:
            print("x", x)
            if x["version"] == 1:
                found_hr = True        
        self.assertTrue(found_hr)

    @unittest.skip("redesign")
    def test_should_receive_device_detail(self):
        client = Client()
        sup = SiteUpdate()
        dtu = DeviceTypeUpdate()
        sdu = SiteDeviceConfUpdate()
        sup.upsert({"id": 998, "name": "abc"})
        dev_type = dtu.upsert(REF_DEVICE_TYPE)
        dev_1 = copy.copy(DEVICE_1)
        dev_1["device_type"] = dev_type.id
        device_cong_data = {"site": 998, "devices": [dev_1]}
        print("Device conf", device_cong_data, dev_type)
        device_conf_obj = sdu.upsert(device_cong_data)
        print("device_conf_obj", device_conf_obj.id, device_conf_obj)
        response = client.get(
            reverse('ahe_mb:devices-detail', kwargs={"pk": device_conf_obj.id}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        print("data_recv", data_recv)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["devices"][0]["name"], "test_device_1")
        self.assertEqual(data_recv["version"], 1)

    @unittest.skip("redesign")
    def test_should_update_device(self):
        client = Client()
        sup = SiteUpdate()
        dtu = DeviceTypeUpdate()
        sdu = SiteDeviceConfUpdate()
        sup.upsert({"id": 998, "name": "abc"})
        dev_type = dtu.upsert(REF_DEVICE_TYPE)
        dev_1 = copy.copy(DEVICE_1)
        dev_1["device_type"] = dev_type.id
        device_cong_data = {"site": 998, "devices": [dev_1]}
        print("Device conf", device_cong_data, dev_type)
        device_conf_obj = sdu.upsert(device_cong_data)
        print("device_conf_obj", device_conf_obj.id, device_conf_obj)
        response = client.get(
            reverse('ahe_mb:devices-detail', kwargs={"pk": device_conf_obj.id}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        print("data_recv", data_recv)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["devices"][0]["name"], "test_device_1")
        self.assertEqual(data_recv["version"], 1)
        data_recv["devices"][0]["port"] = 5020
        response = client.put(
            reverse('ahe_mb:devices-detail', kwargs={"pk": device_conf_obj.id}), json.dumps(data_recv), content_type='application/json')
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv_2 = json.loads(response.content)
        self.assertIsInstance(data_recv_2, dict)
        self.assertEqual(data_recv_2["devices"][0]["name"], "test_device_1")
        self.assertEqual(data_recv_2["devices"][0]["port"], 5020)
        self.assertEqual(data_recv_2["version"], 2)
