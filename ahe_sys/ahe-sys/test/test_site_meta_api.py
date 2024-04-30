from django.test import Client, TestCase
from django.urls import reverse
import json
import unittest
from ahe_sys.update import SiteUpdate, SiteMetaConfUpdate, create_site_args, create_ahe_client


SITE_NAME_TEST = "test runner site 1"
SITE_ID_TEST = 999
SITE_DATA = {"id": SITE_ID_TEST, "name": SITE_NAME_TEST, "client": "test-client"}

SITE_MET_DATA = {"key": "offset", "value": "300", "parent": None}

@unittest.skip("rewrite with new serializer")
class TestSiteMetaAPI(TestCase):
    def setUp(self):
        client = create_ahe_client()
        self.test_site = create_site_args(**SITE_DATA)

    def test_should_receive_meta(self):
        client = Client()
        smu = SiteMetaConfUpdate()
        smu.upsert({"site": SITE_ID_TEST, "detail": [
            {"key": "v2", "value": 1.1, "parent": None}]})
        response = client.get(
            reverse('ahe_sys:meta-list', kwargs={"site_pk": SITE_ID_TEST}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        self.assertEqual(data_recv[0]["site"], SITE_ID_TEST)
        self.assertEqual(data_recv[0]["detail"][0]["key"], "v2")
        self.assertEqual(data_recv[0]["detail"][0]["value"], '1.1')
