import copy
from ahe_common.updates import Update, update_parameters
from ahe_mb.models import BitMap, Enum, Map
from ahe_mb.serializer import BitMapSerializer, EnumSerializer, MapSerializer, SiteDeviceListSerializer, DeviceTypeSerializer
from ahe_sys.update import DeviceTypeUpdate, REF_DEVICE_TYPE, create_device_type, create_site_args


class BitMapUpdate(Update):
    serializer = BitMapSerializer
    query_cols = ["name"]


class EnumUpdate(Update):
    serializer = EnumSerializer
    query_cols = ["name"]


class MapUpdate(Update):
    serializer = MapSerializer
    query_cols = ["name"]


class SiteDeviceConfUpdate(Update):
    serializer = SiteDeviceListSerializer
    query_cols = ["site"]


class DeviceMapUpdate(Update):
    serializer = DeviceTypeSerializer
    query_cols = ["name"]


class SiteDeviceListUpdate(Update):
    serializer = SiteDeviceListSerializer
    query_cols = ["site"]


REF_MODBUS_FIELDS = [
    {'field_address': 0, 'ahe_name': 'var1', 'field_format': 'uint16'},
    {'field_address': 1, 'ahe_name': 'var2', 'field_format': 'uint16'},
    {'field_address': 5, 'ahe_name': 'var3', 'field_format': 'uint16'},
    {'field_address': 240, 'ahe_name': 'var4', 'field_format': 'uint16'},
]

REF_DEVICE_1 = {"name": "test_device_1",
                "ip_address": "127.0.0.1", "port": 5020, "unit": 1}

REF_BITMAP_DATA = {"name": "test_bit_map"}
REF_BIT_VALUE = [
    {"ahe_name": "Bit1", "start_bit": 0, "end_bit": 0, "description": "test_bit_1"},
    {"ahe_name": "Bit2", "start_bit": 1, "end_bit": 1, "description": "test_bit_2"}
]

REF_MAP_DATA = {"name": "test_map1", "fields": REF_MODBUS_FIELDS, "description": "test_map_1"}

REF_DEVICE_TYPE = {
    "name": "Test inv",
    "device_category": "inverter",
    "interface_type": "MODBUS"
}


def create_bitmap(**kwargs):
    allowed_parameters = ("name", "detail")
    data = copy.copy(REF_BITMAP_DATA)
    update_parameters(kwargs, allowed_parameters, data)
    if "detail" not in kwargs:
        data["detail"] = REF_BIT_VALUE
    print("data in create modbus", data, kwargs)
    mu = BitMapUpdate()
    return mu.upsert(data)


def create_modbus_map(**kwargs):
    allowed_parameters = (
        "name", "map_reg", "map_max_read", "read_spaces", "detail", "description")
    data = copy.copy(REF_MAP_DATA)
    update_parameters(kwargs, allowed_parameters, data)
    if "detail" not in kwargs:
        data["detail"] = REF_MODBUS_FIELDS
    print("data in create modbus", data)
    print("kwargs in create modbus", kwargs)
    mu = MapUpdate()
    return mu.upsert(data)


def create_device_conf(**kwargs):
    allowed_parameters = ("detail", "site")
    device_conf_data = {}
    if "site" not in kwargs:
        create_site_args(id=998, name="abc")
        device_conf_data["site"] = 998
    sdu = SiteDeviceConfUpdate()
    if "detail" not in kwargs:
        print("******************* create new modbus map")
        dev = create_device_map()
        dev_1 = copy.copy(REF_DEVICE_1)
        dev_1["device_type"] = dev.id
        device_conf_data["detail"] = [dev_1]
    update_parameters(kwargs, allowed_parameters, device_conf_data)
    print("--calling add Device conf", device_conf_data)
    device_conf_obj = sdu.upsert(device_conf_data)
    return device_conf_obj


# DEVICE_MOD_DATA = {"name": "test_mod", "mod": []}
MAP_MOD_DATA = {"read_spaces": True, "map_reg": "Holding Register",
                "map_max_read": 120, "start_address": 0}


def create_device_map(**kwargs):
    allowed_parameters = (
        "detail", "name", "device_category", "interface_type")
    device_type_data = copy.deepcopy(REF_DEVICE_TYPE)
    if "detail" not in kwargs:
        map_data = copy.deepcopy(REF_MAP_DATA)
        map_obj = create_modbus_map(**map_data)
        print("map", map_obj)
        device_maps = list()
        device_maps.append({"map": map_obj.name})
        device_type_data["detail"] = device_maps
    update_parameters(kwargs, allowed_parameters, device_type_data)
    dtu = DeviceMapUpdate()
    dev = dtu.upsert(device_type_data)
    return dev
