from urllib import response
from django.test import Client, TestCase
from random import randint
from ahe_translate.models import KeyMap
from django.urls import reverse
import json
import copy
import unittest
from django.test.client import encode_multipart, RequestFactory



class TestKeyMapApi(TestCase):

    def setUp(self):
        self.key_map_url = reverse('ahe_translate:keymap')
   
    def test_Keymap_api(self):
        client = Client()
        
        response = client.post(self.key_map_url , [{"key":"AAAA","var":"voltage"}],
                              content_type="application/json")
        key_map_obj = KeyMap.objects.get(var="voltage")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "ok")
        self.assertEqual(key_map_obj.key,"AAAA")

    
    def test_ignore_duplicate_key(self):
        client = Client()
        response = client.post(self.key_map_url , [{"key":"AAAA","var":"voltage"},
                                              {"key":"AAAA","var":"current"}],
                              content_type="application/json")
        key_map_obj = KeyMap.objects.filter(var="voltage")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "ok")
        self.assertEqual(len(key_map_obj),1)
        self.assertEqual(key_map_obj[0].key,"AAAA")
    
    def test_ignore_duplicate_value(self):
        client = Client()
        response = client.post(self.key_map_url , [{"key":"AAAA","var":"current"},
                                              {"key":"AAAB","var":"current"}],
                              content_type="application/json")
        key_map_obj = KeyMap.objects.filter(var="current")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "ok")
        self.assertEqual(len(key_map_obj),1)
        self.assertEqual(key_map_obj[0].key,"AAAA")
    
    def test_ignore_duplicate_key_value(self):
        client = Client()
        response = client.post(self.key_map_url , [{"key":"AAAA","var":"power"},
                                              {"key":"AAAA","var":"power"}],
                              content_type="application/json")
        key_map_obj = KeyMap.objects.filter(var="power")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "ok")
        self.assertEqual(len(key_map_obj),1)
        self.assertEqual(key_map_obj[0].key,"AAAA")
