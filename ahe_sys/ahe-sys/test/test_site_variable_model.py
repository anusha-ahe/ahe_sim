from django.test import TestCase
import unittest
from ahe_sys.models import Site, SiteVariableList, Variable
from ahe_sys.update import SiteUpdate, SiteVariableListUpdate, create_ahe_client, create_site_args
import copy

TEST_SITE_ID = 998
site_variable = {"site": TEST_SITE_ID, "version": 1, "detail": [
    {"name": "abc"},
    {"name": "def"}]}


class TestSiteVariableUpdate(TestCase):

    @unittest.skip("rewrite with new serializer")
    def test_should_create_variable_conf(self):
        create_ahe_client()
        self.test_site = create_site_args(id=TEST_SITE_ID, name="t1")        
        smu = SiteVariableListUpdate()
        vars = smu.upsert(site_variable)
        self.assertEqual(vars.site.id, TEST_SITE_ID)
        self.assertEqual(vars.version, 1)

    @unittest.skip("rewrite with new serializer")
    def test_should_update_metadata(self):
        create_ahe_client()
        self.test_site = create_site_args(id=TEST_SITE_ID, name="t1")        
        smu = SiteVariableListUpdate()
        smu_data = smu.upsert(site_variable)
        print("smu data", smu_data)
        new_meta = copy.deepcopy(site_variable)
        new_meta["detail"][1]["name"] = "aaa"
        new_meta["id"] = smu_data.id
        print("--calling update")
        new_smu_data = smu.upsert(new_meta)
        print("--nn", new_smu_data, new_smu_data.version)
        self.assertEqual(new_smu_data.version, 2)
