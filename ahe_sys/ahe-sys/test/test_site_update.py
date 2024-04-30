from django.test import Client, TestCase
from ahe_sys.update import SiteUpdate, create_site_args, REF_SITE, create_ahe_client
from ahe_sys.models import Site
import unittest


class TestSiteUpdate(TestCase):

    def test_site_is_created(self):
        create_ahe_client()
        site = create_site_args()        
        print(site)
        self.assertIsInstance(site, Site)

    def test_site_name_is_required(self):
        su = SiteUpdate()
        with self.assertRaises(ValueError):
            site = su.upsert({"id": 998})

    def test_site_id_is_required(self):
        su = SiteUpdate()
        with self.assertRaises(KeyError):
            site = su.upsert({"name": "abc"})

    def test_site_name_is_updated(self):
        create_ahe_client()
        s1 = create_site_args(id=998, name="abcd")        
        self.assertEqual(s1.name, "abcd")
        su = SiteUpdate()
        su.upsert({"id": 998, "name": "abcd1"})
        s2 = Site.objects.filter(id=998).first()
        self.assertEqual(s2.name, "abcd1")

    def test_create_function(self):
        create_ahe_client()
        s1 = create_site_args()        
        self.assertEqual(s1.name, REF_SITE["name"])
