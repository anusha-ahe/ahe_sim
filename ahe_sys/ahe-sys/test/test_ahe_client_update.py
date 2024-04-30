from django.test import Client, TestCase
from django.urls import reverse
import json
from ahe_sys.update import create_ahe_client, create_site_args
from ahe_sys.models import AheClient
from django.core.exceptions import ValidationError

# test update
# update should set correct start site_id
# api to list client
# api to create a client
# api to update a client


class TestAheClient(TestCase):
    def test_ahe_client_is_created(self):
        client = create_ahe_client()
        print(client)
        self.assertIsInstance(client, AheClient)

    def test_ahe_client_with_invalid_name(self):
        with self.assertRaises(ValidationError):
            client = create_ahe_client(name="test_ client")

    def test_ahe_client_with_valid_start_id(self):
        client1 = create_ahe_client(name="a")
        client2 = create_ahe_client(naem="b")
        print(client1, client2)
        self.assertNotEqual(client1.start_site_id, client2.start_site_id)

    def test_ahe_client_with_valid_end_id(self):
        client1 = create_ahe_client()
        print(client1)
        self.assertEqual(client1.end_site_id - client1.start_site_id, 199 )


    def test_ahe_client_should_skip_site(self):
        client = create_ahe_client()
        site = create_site_args(id=410)
        client = create_ahe_client(name="test-client2")
        print(client)
        self.assertEqual(client.start_site_id, 601)
