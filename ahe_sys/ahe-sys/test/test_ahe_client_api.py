from django.test import Client, TestCase
from django.urls import reverse
import json
import unittest
from ahe_sys.update import create_ahe_client, REF_CLIENT
from ahe_sys.models import AheClient


class TestClientUpdateAPI(TestCase):
    def setUp(self):
        self.test_client = create_ahe_client()

    def test_should_receive_clients(self):
        client = Client()
        response = client.get(reverse('ahe_sys:client-list'))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        success = False
        for data in data_recv:
            if data["name"] == REF_CLIENT["name"]:
                success = True
        self.assertTrue(success)

    def test_should_receive_single_client(self):
        client = Client()
        response = client.get(reverse('ahe_sys:client-detail', kwargs={"pk": self.test_client.id}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], REF_CLIENT["name"])

    def test_should_receive_update_client(self):
        client = Client()
        response = client.get(reverse('ahe_sys:client-detail', kwargs={"pk": self.test_client.id}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        data_recv["name"] = "test-runner-client-2"
        response = client.put(reverse('ahe_sys:client-detail', kwargs={"pk": self.test_client.id}), json.dumps(data_recv),content_type='application/json')
        print("response is ", response.content)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, dict)
        self.assertEqual(data_recv["name"], "test-runner-client-2")
        obj = AheClient.objects.get(name="test-runner-client-2")
        self.assertEqual(obj.id, self.test_client.id)
