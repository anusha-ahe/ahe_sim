from django.test import TestCase
from ahe_sys.update import DeviceTypeUpdate, create_device_type, REF_DEVICE_TYPE, update_device_type
from ahe_sys.models import DeviceType
import copy


class TestDeviceTypeUpdate(TestCase):

    def test_should_add_device_type(self):
        dt = create_device_type()
        self.assertEqual(dt.name, REF_DEVICE_TYPE["name"])
        self.assertEqual(dt.device_category, REF_DEVICE_TYPE["device_category"])
        self.assertEqual(dt.interface_type, REF_DEVICE_TYPE["interface_type"])

    def test_should_add_device_type_with_param(self):
        dt = create_device_type(device_category="grid")
        self.assertEqual(dt.name, REF_DEVICE_TYPE["name"])
        self.assertEqual(dt.device_category, "grid")
        self.assertEqual(dt.interface_type, REF_DEVICE_TYPE["interface_type"])

    def test_should_change_device_type(self):
        dtu = DeviceTypeUpdate()
        dev_type1 = create_device_type()
        print("dev", dev_type1)
        dtd_new = copy.deepcopy(REF_DEVICE_TYPE)
        # id is required for update
        dtd_new["id"] = dev_type1.id
        dtd_new["name"] = "Trumph 2"
        dev_type2 = dtu.upsert(dtd_new)
        self.assertEqual(dev_type2.name, "Trumph 2")

    def test_should_update_device_type(self):
        dev_type1 = create_device_type()
        dev_type2 = update_device_type(dev_type1.id, name="Trumph 2")
        self.assertEqual(dev_type2.name, "Trumph 2")

