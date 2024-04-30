# from base64 import encode
# from curses import meta
# from distutils.log import error
# from importlib.metadata import metadata
# from urllib import response
# from django.test import Client, TestCase
# from random import randint
# from ahe_sys.models import Site
# from django.urls import reverse
# import json
# from django.test.client import encode_multipart, RequestFactory
# from ahe_sys.update import SiteUpdate, SiteMetaConfUpdate, create_site_args
# from django.core.exceptions import ValidationError


# SITE_NAME_TEST = "test runner site 1"
# SITE_ID_TEST = 999
# SITE_DATA = {"id": SITE_ID_TEST, "name": SITE_NAME_TEST, "client": "test-client"}
# # SITE_DATA_ERROR_1 = {"id": SITE_ID_TEST, "name": SITE_NAME_TEST}
# # SITE_DATA_MISSING_KEY = {"id": SITE_ID_TEST, "name": SITE_NAME_TEST}
# # SITE_MET_DATA = {"key": "offset", "value": "300", "parent": None}


# class TestSiteAPI(TestCase):
#     def setUp(self):
#         su = SiteUpdate()
#         self.test_site = create_site_args(**SITE_DATA)

#     def test_site_deletion_should_fail(self):
#         print(self.test_site)
#         with self.assertRaises(ValidationError) as context:
#             print(context)
#             self.test_site.delete()

#     # def test_should_receive_single_site_data(self):
#     #     client = Client()
#     #     response = client.get(
#     #         reverse('ahe_sys:all-sites') + "/" + str(SITE_ID_TEST))
#     #     print("response is ", response.content)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(SITE_DATA, json.loads(response.content))

#     # def test_should_receive_all_site_data(self):
#     #     client = Client()
#     #     print(reverse('ahe_sys:all-sites'))
#     #     response = client.get(reverse('ahe_sys:all-sites'))
#     #     print("response is ", response.content)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertIn(SITE_DATA, json.loads(response.content))

#     # def test_should_update_key(self):
#     #     client = Client()
#     #     update_site_url = reverse('ahe_sys:update-site', kwargs={'pk': 999})
#     #     print("PUT call url", update_site_url)
#     #     response = client.put(update_site_url, SITE_DATA,
#     #                           content_type="application/json")
#     #     print("response is", response.content)
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertEqual(response.json(), SITE_DATA)
