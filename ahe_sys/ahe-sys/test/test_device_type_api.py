from django.test import Client, TestCase
from django.urls import reverse
import json


DEVICE_TYPE_DATA = {'name': 'Test Inv',
                    'device_category': 'inverter', 'interface_type': 'MODBUS'}


class TestSiteAPI(TestCase):

    def test_device_type_list_api(self):
        client = Client()
        device_type_url = reverse('ahe_sys:device-list')
        print("url for ahe_sys:device-list", device_type_url)
        response = client.post(device_type_url, DEVICE_TYPE_DATA,
                               content_type="application/json")
        print("response is ", response.content)
        self.assertEqual(response.status_code, 201)
        resp_data = json.loads(response.content)
        self.assertIsInstance(resp_data, dict)
        self.assertIn('device_category', resp_data)
        self.assertIn('interface_type', resp_data)
        self.assertIn('name', resp_data)
        self.assertIn('id', resp_data)
        self.assertEqual(resp_data['name'], DEVICE_TYPE_DATA['name'])
        self.assertEqual(resp_data['device_category'],
                         DEVICE_TYPE_DATA['device_category'])
        self.assertEqual(resp_data['interface_type'],
                         DEVICE_TYPE_DATA['interface_type'])
        response2 = client.get(reverse('ahe_sys:device-list'))
        self.assertEqual(response2.status_code, 200)
        print("response2 is ", response2.content)
        resp_data2 = json.loads(response2.content)
        self.assertIsInstance(resp_data2, list)
        self.assertIn(resp_data, resp_data2)
