import copy
from django.test import TestCase
from ahe_mb.update import SiteDeviceConfUpdate, REF_DEVICE_1
from ahe_sys.update import SiteUpdate, DeviceTypeUpdate, REF_DEVICE_TYPE
import unittest



class TestDeviceMapUpdate(TestCase):

    @unittest.skip("redesign")
    def test_should_create_device(self):
        sup = SiteUpdate()
        dtu = DeviceTypeUpdate()
        sdu = SiteDeviceConfUpdate()
        sup.upsert({"id": 998, "name": "abc"})
        dev_type = dtu.add(REF_DEVICE_TYPE)
        dev_1 = copy.copy(REF_DEVICE_1)
        dev_1["device_type"] = dev_type.id
        device_cong_data = {"site": 998, "devices": [dev_1]}
        print("Device conf", device_cong_data, dev_type)
        device_conf_obj = sdu.add(device_cong_data)
        devices = device_conf_obj.devices.all()
        print("devices", device_conf_obj, devices)
        self.assertEqual(devices[0].name, "test_device_1")
        # self.assertEqual(devices.name, "bm1")
        self.assertEqual(device_conf_obj.version, 1)
        self.assertGreaterEqual(len(devices), 1)

    @unittest.skip("redesign")
    def test_should_update_device(self):
        sup = SiteUpdate()
        dtu = DeviceTypeUpdate()
        sdu = SiteDeviceConfUpdate()
        sup.upsert({"id": 998, "name": "abc"})
        dev_type = dtu.add(REF_DEVICE_TYPE)
        dev_1 = copy.copy(REF_DEVICE_1)
        dev_1["device_type"] = dev_type.id
        device_conf_data = {"site": 998, "devices": [dev_1]}
        print("--calling add Device conf", device_conf_data, dev_type)
        device_conf_obj = sdu.add(device_conf_data)
        devices = device_conf_obj.devices.all()
        print("devices", device_conf_obj, devices)

        device_cong_data_2 = copy.deepcopy(device_conf_data)
        device_cong_data_2["devices"][0]["port"] = 2
        device_cong_data_2["id"] = device_conf_obj.id
        print("--calling update", device_cong_data_2)
        device_conf_obj_2 = sdu.update(device_cong_data_2)
        print("--nn", device_conf_obj_2)
        devices = device_conf_obj_2.devices.all()
        self.assertEqual(devices[0].port, 2)
        self.assertEqual(device_conf_obj.version, 1)




