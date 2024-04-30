from django.test import Client, TestCase
from django.urls import reverse
import json
import unittest
from ahe_sys.update import SiteUpdate, SiteMetaConfUpdate, DeviceTypeUpdate, create_site_args, create_ahe_client
from ahe_sys.models import DeviceType

SITE_NAME_TEST = "test runner site 1"
SITE_ID_TEST = 999
SITE_DATA = {"id": SITE_ID_TEST, "name": SITE_NAME_TEST, "client": "test-client"}
SITE_MET_DATA = {"key": "offset", "value": "300", "parent": None}
DEVICE_TYPE_DATA = {"name": "Test Inverter",
                    "device_category": "inverter",
                    "interface_type": "MODBUS"}


class TestDeviceTypeAPI(TestCase):
    def test_all_url_lookup(self):
        client = create_ahe_client()
        self.test_site = create_site_args(**SITE_DATA)
        print("url for ahe_sys:site-list",
              reverse('ahe_sys:site-list'))
        print("url for ahe_sys:device-list",
              reverse('ahe_sys:device-list'))
        print("url for ahe_sys:meta-list",
              reverse('ahe_sys:meta-list', kwargs={"site_pk": SITE_ID_TEST}))
        # print("url for ahe_sys:dev-list",
        #       reverse('ahe_sys:dev-list', kwargs={"site_pk": SITE_ID_TEST}))
        print("url for ahe_sys:var-list",
              reverse('ahe_sys:var-list', kwargs={"site_pk": SITE_ID_TEST}))

    def test_device_type_list_api(self):
        client = Client()
        dtu = DeviceTypeUpdate()
        dev_type = dtu.upsert(DEVICE_TYPE_DATA)
        dev_url = reverse('ahe_sys:device-list')
        print("url", dev_url)
        response = client.get(dev_url)
        print("resp is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        for data in data_recv:
            if data["name"] == "Test Inverter":
                return
        self.fail("")

    @unittest.skip("Move to mb")
    def test_site_device_list_api(self):
        client = Client()
        su = SiteUpdate()
        site = su.update(SITE_DATA)
        print(site)
        dtu = DeviceTypeUpdate()
        dev_type = dtu.add(DEVICE_TYPE_DATA)
        print("dev_type", dev_type)
        sdcu = SiteDeviceListUpdate()
        site_dev_conf = sdcu.add({"site": site.id, "site_device": [
                                 {"device_name": "inverter_1", "device_type": dev_type.id}]})
        print("site_dev_conf", site_dev_conf)
        dd = sdcu.get(site_dev_conf.id)
        print(dd)
        dev_url = reverse('ahe_sys:dev-list', kwargs={"site_pk": SITE_ID_TEST})
        print("url", dev_url)
        response = client.get(dev_url)
        print("resp is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        print("data_recv", data_recv)
        for data in data_recv[0]["site_device"]:
            if data["device_name"] == "inverter_1":
                return
        self.fail("")
