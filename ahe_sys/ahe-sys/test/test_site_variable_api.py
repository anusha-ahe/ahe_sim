from django.test import Client, TestCase
from django.urls import reverse
import json
import unittest
from ahe_sys.update import SiteUpdate, SiteVariableListUpdate, create_site_args, create_ahe_client


SITE_NAME_TEST = "test runner site 1"
SITE_ID_TEST = 999
SITE_DATA = {"id": SITE_ID_TEST, "name": SITE_NAME_TEST}

site_variable = {"site": SITE_ID_TEST,
                 "version": 1,
                 "detail": [
                     {"name": "abc"},
                     {"name": "def"}]}


class TestSiteVariablesAPI(TestCase):
    def setUp(self):
        create_ahe_client()
        self.test_site = create_site_args(**SITE_DATA)

    @unittest.skip("rewrite with new serializer")
    def test_should_receive_variables(self):
        client = Client()
        smu = SiteVariableListUpdate()
        smu.upsert(site_variable)
        response = client.get(
            reverse('ahe_sys:var-list', kwargs={"site_pk": SITE_ID_TEST}))
        print("response is ", response.content)
        self.assertEqual(response.status_code, 200)
        data_recv = json.loads(response.content)
        self.assertIsInstance(data_recv, list)
        self.assertEqual(data_recv[0]["site"], SITE_ID_TEST)
        self.assertEqual(data_recv[0]["detail"][0]["name"], "abc")
