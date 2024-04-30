from django.test import TestCase
import unittest
from ahe_sys.models import Site, SiteMeta, read_metadata, convert_to_value
from ahe_sys.update import SiteUpdate, SiteMetaConfUpdate, create_site_args, create_ahe_client
from ahe_sys.views import SiteMetaConfViewSet
from ahe_sys.serializer import SiteMetaConfSerializer
import copy

TEST_SITE_ID = 998
REF_SITE_META = {"site": "t10", "version": 1, "detail": [
    {"key": "abc", "value": 1.3, "parent": None},
    {"key": "def", "value": 456, "parent": "abc"}]}


class TestSiteUpdate(TestCase):

    @unittest.skip("rewrite with new serializer")
    def test_should_create_meta(self):
        create_ahe_client()
        create_site_args(id=TEST_SITE_ID, name="t1")
        smu = SiteMetaConfUpdate()
        meta = smu.upsert(REF_SITE_META)
        self.assertEqual(meta.site.id, TEST_SITE_ID)
        self.assertEqual(meta.version, 1)

    @unittest.skip("rewrite with new serializer")
    def test_should_update_metadata(self):
        create_ahe_client()
        create_site_args(id=TEST_SITE_ID, name="t1")        
        smu = SiteMetaConfUpdate()
        smu_data = smu.upsert(REF_SITE_META)
        print("smu data", smu_data)
        data = read_metadata(TEST_SITE_ID)
        self.assertEqual(data, {"abc": {"def": 456}})
        new_meta = copy.deepcopy(REF_SITE_META)
        new_meta["detail"][1]["value"] = 111
        new_meta["id"] = smu_data.id
        print("--calling update")
        new_smu_data = smu.upsert(new_meta)
        print("--nn", new_smu_data, new_smu_data.version)
        new_data = read_metadata(TEST_SITE_ID)
        self.assertEqual(new_data, {"abc": {"def": 111}})

    @unittest.skip("rewrite with new serializer")
    def test_generated_metadata_dict(self):
        create_ahe_client()
        create_site_args(id=TEST_SITE_ID, name="t10")        
        smu = SiteMetaConfUpdate()
        smu_data = smu.upsert(REF_SITE_META)
        print("smu data", smu_data)
        data = read_metadata(TEST_SITE_ID)
        self.assertEqual(data, {"abc": {"def": 456}})

    def test_convert_to_value(self):
        self.assertTrue(convert_to_value("True"))
        self.assertFalse(convert_to_value("False"))
        self.assertIsNone(convert_to_value(None))
        self.assertEqual(convert_to_value("100"), 100)
        self.assertEqual(convert_to_value("1.23"), 1.23)

    @unittest.skip("rewrite with new serializer")
    def test_should_get_dict(self):
        create_ahe_client()
        create_site_args(id=TEST_SITE_ID, name="t1")        
        smu = SiteMetaConfUpdate()
        smu_data = smu.upsert(REF_SITE_META)
        data_dict = smu.get(smu_data.id)
        print("smu_data", smu_data, data_dict)
        self.assertIsInstance(data_dict, dict)
        self.assertEqual(data_dict["id"], smu_data.id)
        self.assertIsInstance(data_dict["detail"], list)
