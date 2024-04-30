import copy
from ahe_mb.models import Field, Map
from ahe_sys.update import SiteUpdate, REF_DEVICE_TYPE
from ahe_mb.update import MapUpdate, SiteDeviceConfUpdate, REF_MODBUS_FIELDS, create_modbus_map, REF_DEVICE_1


TEST_MOBUS_EVENTS = [
    {"id": 11, "name": "events_1", "description": "Events 1", "func": "EQUAL",
     "variable": "events_1", "param": 1, "level": "Alarm"},
    {"id": 12, "name": "events_2", "description": "Events 2", "func": "EQUAL",
     "variable": "events_2", "param": 1, "level": "Alarm"}
]


def create_test_field(**kwargs):
    field_params = {'field_address': 0,
                    'field_format': 'uint16'}
    field_params.update(**kwargs)
    fld = Field(**field_params)
    fld.save()
    return fld


def create_test_devices():
    modbus_map = create_modbus_map(name="test_mb_map")
    sup = SiteUpdate()
    sdu = SiteDeviceConfUpdate()
    sup.upsert({"id": 998, "name": "abc"})
    dev_1 = copy.copy(REF_DEVICE_1)
    dev_1["device_type"] = modbus_map.device_type.id
    device_conf_data = {"site": 998, "devices": [dev_1]}
    print("--calling add Device conf", device_conf_data, modbus_map.device_type)
    device_conf_obj = sdu.add(device_conf_data)
    return device_conf_obj


# def create_test_device_with_coil(device_name, modbus_map, site, **kwargs) -> ModbusDevice:
#     ModbusDevice.objects.filter(name=device_name).delete()
#     device_params = {'ip_address': '127.0.0.1',
#                      'port': 5020,
#                      'unit': 1,
#                      'start_address': 0,
#                      'map': modbus_map,
#                      'site': site,
#                      'name': device_name}

#     device_params.update(**kwargs)
#     device_obj = ModbusDevice.objects.create(**device_params)
#     device_obj.save()
#     return device_obj


# def create_test_events(site, modbus_name):
#     # Map.objects.filter(name=modbus_name).delete()
#     dtu = DeviceTypeUpdate()
#     dev_type = dtu.add_device_type("TEST inverter", "inverter", "MODBUS")

#     modbus_map = Map.objects.get_or_create(
#         name=modbus_name, device_type=dev_type)[0]
#     device = create_test_device(
#         'test', modbus_map, site, start_address=1)
#     for map_events in TEST_MOBUS_EVENTS:
#         map_events["map"] = modbus_map
#         map_events["device"] = device
#         map_events = ModbusMapEvents(**map_events)
#         map_events.save()
