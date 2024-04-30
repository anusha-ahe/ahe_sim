import copy
from ahe_common.updates import Update, update_parameters
from ahe_sys.models import Site, Variable, DeviceType, SiteMetaConf, SiteVariableList, AheClient
from ahe_sys.serializer import SiteSerializer, SiteMetaConfSerializer,  \
    SiteVariableListSerializer, DeviceTypeListSerializer, AheClientSerializer, CLIENT_COLUMNS, SITE_COLUMNS, DEVICE_TYPE_COLUMNS


REF_SITE = {"id": 888, "name": "Test Site", "client": "test-client"}

REF_DEVICE_TYPE = {
    "name": "Trumph",
    "device_category": "inverter",
    "interface_type": "MODBUS"
}

REF_CLIENT = {"name": "test-client"}

class AheClientUpdate(Update):
    serializer = AheClientSerializer
    query_cols = ["name"]

class SiteUpdate(Update):
    serializer = SiteSerializer
    query_cols = ["id"]


class SiteMetaConfUpdate(Update):
    serializer = SiteMetaConfSerializer
    query_cols = ["site"]


class SiteVariableListUpdate(Update):
    serializer = SiteVariableListSerializer
    query_cols = ["site"]


class DeviceTypeUpdate(Update):
    serializer = DeviceTypeListSerializer
    query_cols = ["name", "device_category", "interface_type"]


def create_site(site_id, site_name) -> Site:
    print("******          Do not use create_site it is Deprecated        *****")
    su = SiteUpdate()
    return su.update({"id": site_id, "name": site_name})

def create_site_args(**kwargs) -> Site:
    allowed_parameters = SITE_COLUMNS
    su = SiteUpdate()
    data = copy.copy(REF_SITE)
    update_parameters(kwargs, allowed_parameters, data)
    print("create_site_args",data)
    create_ahe_client()
    data["client"] = AheClient.objects.get(name=data["client"]).id
    if "uuid" in data and data["uuid"] == "":
        data["uuid"] = None
    return su.upsert(data)

def create_device_type(**kwargs):
    allowed_parameters = DEVICE_TYPE_COLUMNS
    dtu = DeviceTypeUpdate()
    data = copy.copy(REF_DEVICE_TYPE)
    update_parameters(kwargs, allowed_parameters, data)
    return dtu.upsert(data)

def update_device_type(id, **kwargs):
    allowed_parameters = ("name", "device_category", "interface_type")
    dtu = DeviceTypeUpdate()
    data = dtu.get(id)
    update_parameters(kwargs, allowed_parameters, data)
    return dtu.upsert(data)

def create_ahe_client(**kwargs):
    allowed_parameters = CLIENT_COLUMNS
    su = AheClientUpdate()
    data = copy.copy(REF_CLIENT)
    update_parameters(kwargs, allowed_parameters, data)
    return su.upsert(data)
