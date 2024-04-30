from django.test import Client, TestCase
# from ahe_sys.update import SiteUpdate, SiteDeviceListUpdate, DeviceTypeUpdate
from ahe_sys.models import Site, SiteDeviceList
import unittest


DEVICE_TYPE_DICT = {
    "name": "Trumph",
    "device_category": "inverter",
    "interface_type": "MODBUS"
}


# class TestSiteDeviceListUpdate(TestCase):

#     def test_site_device_list_is_created(self):
#         su = SiteUpdate()
#         site = su.add({"id": 998, "name": "abcd"})
#         print(site)
#         sdcu = SiteDeviceListUpdate()
#         site_dev_conf = sdcu.add(
#             {"site": site.id, "version": 1, "site_device": []})
#         self.assertIsInstance(site_dev_conf, SiteDeviceList)

#     def test_site_device_list_is_created_with_default_version(self):
#         su = SiteUpdate()
#         site = su.update({"id": 998, "name": "abcd"})
#         print(site)
#         sdcu = SiteDeviceListUpdate()
#         site_dev_conf = sdcu.add({"site": site.id, "site_device": []})
#         self.assertIsInstance(site_dev_conf, SiteDeviceList)
#         self.assertEqual(site_dev_conf.version, 1)

#     def test_site_device_list_is_updated_with_next_version(self):
#         su = SiteUpdate()
#         site = su.update({"id": 998, "name": "abcd"})
#         print(site)
#         sdcu = SiteDeviceListUpdate()
#         site_dev_conf_1 = sdcu.add({"site": site.id, "site_device": []})
#         site_dev_conf_2 = sdcu.update({"site": site.id, "site_device": []})
#         print(site_dev_conf_2)
#         self.assertEqual(site_dev_conf_2.version, 2)

#     def test_should_create_site_device_list_with_device(self):
#         su = SiteUpdate()
#         site = su.update({"id": 998, "name": "abcd"})
#         print(site)
#         dtu = DeviceTypeUpdate()
#         dt = dtu.add(DEVICE_TYPE_DICT)
#         print(dt)
#         sdcu = SiteDeviceListUpdate()
#         site_dev_conf = sdcu.add({"site": site.id, "site_device": [
#                                  {"device_name": "inv", "device_type": dt.id}]})
#         print("site_dev_conf", site_dev_conf)
#         dd = sdcu.get(site_dev_conf.id)
#         print(dd)
#         self.assertIsInstance(site_dev_conf, SiteDeviceList)
#         self.assertEqual(site_dev_conf.version, 1)
#         self.assertEqual(dd["site_device"][0]["device_name"], "inv")
#         self.assertEqual(dd["site_device"][0]["device_type"], dt.id)
