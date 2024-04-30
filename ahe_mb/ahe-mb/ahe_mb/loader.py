import re
from threading import Condition
from django.db import transaction
from ahe_sys.common.loader import Row, FileLoader, is_address_overlaping, ALREADY_USED
from ahe_sys.models import DeviceType, DEVICE_CATEGORY, SiteDeviceList
from ahe_mb.models import ENCODINGS, FORMATS, BitMap, BitValue, Map, Field, REGISTER_TYPES, \
    Enum, EnumValue, DeviceMap, SiteDevice
from ahe_mb.update import BitMapUpdate, EnumUpdate, MapUpdate, DeviceMapUpdate, SiteDeviceListUpdate

# TODO remove modbus map name from map upload
# TODO add device type from the file
# TODO move test to ahe_sys


class BitRow(Row):
    ROW_FIELDS = ["ahe_name", "start_bit", "end_bit", "description"]
    REQUIRED_COLUMNS = ["bit_map", "ahe_name", "start_bit", "end_bit"]
    NONE_BLANK_COLUMNS = ["bit_map", "ahe_name", "start_bit", "end_bit"]
    NAME_FIELDS = ["bit_map", "ahe_name"]
    INT_FIELDS = ["start_bit", "end_bit"]
    RANGE_FIELDS = {
        "start_bit": {"min": 0, "max": 15},
        "end_bit": {"min": 0, "max": 15},
    }
    FIELD_RELATIVE = {"end_bit": {">=": "start_bit"}}
    KEY_GENERATION_COLS = ["bit_map"]

    def __init__(self, data) -> None:
        super().__init__(data)

    def get_data(self, bm):
        data = self.get_row_field_data()
        data["bit_map"] = bm
        return data


class BitMapLoader(FileLoader):
    UNIQUE_FIELDS = ["ahe_name", "start_bit", "end_bit"]
    OVERLAP_FIELDS = [("start_bit", "end_bit")]
    row_processing_class = BitRow
    row_class = BitValue
    row_master_key = "bit_map"
    master_class = BitMap
    update_class = BitMapUpdate

    def __init__(self) -> None:
        super().__init__()


class EnumRow(Row):
    ROW_FIELDS = ["enum", "ahe_name", "value", "description"]
    REQUIRED_COLUMNS = ["enum", "ahe_name", "value"]
    NONE_BLANK_COLUMNS = ["enum", "ahe_name", "value"]
    NAME_FIELDS = ["enum", "ahe_name"]
    INT_FIELDS = ["value"]
    INVALID_OPTIONS = {
        "value": [0],
    }
    KEY_GENERATION_COLS = ["enum"]

    def __init__(self, data) -> None:
        super().__init__(data)

    def get_data(self, enum):
        data = self.get_row_field_data()
        data["enum"] = enum
        return data


class EnumLoader(FileLoader):
    UNIQUE_FIELDS = ["ahe_name", "value"]
    row_processing_class = EnumRow
    row_class = EnumValue
    row_master_key = "enum"
    master_class = Enum
    update_class = EnumUpdate

    def __init__(self) -> None:
        super().__init__()


class ModbusRow(Row):
    model = Field
    ROW_FIELDS = ["map", "ahe_name", "description", "field_address", "field_encoding", "field_format", "field_scale",
                  "field_offset", "field_size", "min_value", "max_value", "bit_map", "measure_unit"]
    REQUIRED_COLUMNS = ["modbus_map", "field_address", "field_format", "field_scale", "field_offset", "ahe_name"]
    NONE_BLANK_COLUMNS = ["modbus_map", "field_address", "field_format", "field_scale", "field_offset"]
    NAME_FIELDS = ["modbus_map", "ahe_name", "field_format"]
    INT_FIELDS = ["map_max_read", "field_address", "field_size"]
    FLOAT_FIELDS = ["field_scale", "field_offset", "min_value", "max_value"]
    RANGE_FIELDS = {
        "map_max_read": {"min": 2, "max": 120},
        "field_address": {"min": 0, "max": 99999},
        # "read_spaces": {"min": 0, "max": 1}
    }
    KEY_GENERATION_COLS = ["modbus_map"]
    VALID_OPTIONS = {
        "map_reg": [r[0] for r in REGISTER_TYPES],
        "field_encoding": [r[0] for r in ENCODINGS],
        "field_format": [r[0] for r in FORMATS],
        "read_spaces": ['True', 'False', 'TRUE', 'FALSE'],
    }
    INVALID_OPTIONS = {
        "field_scale": [0],
    }
    INVALID_COMBINATION = [
        {"field": "ahe_name", "condition": {
            "bit_map": "None"}, "choices": ["", None]},
    ]
    VALID_COMBINATION = [
        {"field": "field_scale", "condition": {
            "bit_map": "Not None"}, "choices": ["1", 1, 1.0]},
        {"field": "field_scale", "condition": {
            "field_format": "float32"}, "choices": ["1", 1, 1.0, "-1", -1]},
        {"field": "field_offset", "condition": {
            "field_format": "float32"}, "choices": ["0", 0, 0.0]},
    ]
    CHAR_FIELDS = ["device_category"]

    def __init__(self, data) -> None:
        super().__init__(data)


class ModbusLoader(FileLoader):
    UNIQUE_FIELDS = ["ahe_name", "field_address"]
    row_processing_class = ModbusRow
    row_class = Field
    row_master_key = "map"
    master_class = Map
    update_class = MapUpdate

    def __init__(self) -> None:
        super().__init__()

            
class DeviceMapRow(Row):
    model = DeviceMap
    # ROW_FIELDS = ['device_name', "device_type", "map", "read_spaces", "map_reg", "map_max_read", "start_address"]
    ROW_FIELDS = ["device_type", "map", "read_spaces", "map_reg", "map_max_read", "start_address"]
    REQUIRED_COLUMNS = ["name", "map", "start_address", "device_category"]
    NONE_BLANK_COLUMNS = ["name", "map", "start_address", "device_category"]
    INT_FIELDS = ["start_address"]
    KEY_GENERATION_COLS = ["name", "device_category"]
    VALID_OPTIONS = {
        "map_reg": [r[0] for r in REGISTER_TYPES],
        "read_spaces": ['True', 'False', 'TRUE', 'FALSE'],
        "device_category": [r[0] for r in DEVICE_CATEGORY],
    }
    RANGE_FIELDS = {
        "map_max_read": {"min": 1, "max": 125}
    }

    def __init__(self, data) -> None:
        super().__init__(data)

    def get_data(self, enum):
        data = self.get_row_field_data()
        data["detail"] = enum
        return data

class DeviceMapLoader(FileLoader):
    # UNIQUE_FIELDS = ["name", "map", "start_address", "map_reg"]
    MASTER_FIELDS = ['name', 'device_category','interface_type']
    row_processing_class = DeviceMapRow
    row_class = DeviceMap
    row_master_key = "device_type"
    master_class = DeviceType
    update_class = DeviceMapUpdate

    def __init__(self) -> None:
        super().__init__()

class SiteDeviceRow(Row):
    model = SiteDevice
    # ROW_FIELDS = ['device_name', "device_type", "map", "read_spaces", "map_reg", "map_max_read", "start_address"]
    ROW_FIELDS = ["name", "device_type", "ip_address", "port", "unit", "data_hold_period"]
    REQUIRED_COLUMNS = ["site", "name", "device_type", "ip_address", "port", "unit"]
    NONE_BLANK_COLUMNS = ["site", "name", "device_type", "ip_address", "port", "unit"]
    INT_FIELDS = ["site", "port", "unit"]
    KEY_GENERATION_COLS = ["site"]
    RANGE_FIELDS = {
        "unit": {"min": 1, "max": 247}
    }

    def __init__(self, data) -> None:
        super().__init__(data)

    def get_data(self, enum):
        data = self.get_row_field_data()
        data["detail"] = enum
        return data


class SiteDeviceLoader(FileLoader):
    # UNIQUE_FIELDS = ["name", "map", "start_address", "map_reg"]
    MASTER_FIELDS = ['site']
    row_processing_class = SiteDeviceRow
    row_class = SiteDevice
    row_master_key = "site_device_conf"
    master_class = SiteDeviceList
    update_class = SiteDeviceListUpdate

    def __init__(self) -> None:
        super().__init__()
