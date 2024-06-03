import ahe_sys
import os
import time
from django.conf import settings
from django.forms.models import model_to_dict
import django
import importlib
import ahe_log
import ahe_mb
import requests

MODBUS_SERVER_URL = "http://10.10.8.8:8002/ahe-mb/download-maps"

if not settings.configured:
    settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
    print("Using setting file:", settings_file)
    settings_module = importlib.import_module(settings_file)
    django.setup()


def ahe_open(data_config, mode, params):
    print("device in open", data_config, type(data_config))
    if type(data_config) == ahe_mb.models.SiteDevice:
        return ahe_mb.master.ModbusMaster(data_config, mode, params)
    else:
        return None


def convert_obj_to_dict(obj):
    obj_dict = model_to_dict(obj)
    obj_dict.pop("id", None)
    return obj_dict


def copy_mb_devices(site_id, dest_site_id):
    try:
        mb_devices = []
        modbus_devices = ahe_mb.models.ModbusDevice.objects.filter(
            site=dest_site_id)
        if not modbus_devices:
            return {"modbus_devices": []}
        for modbus_device in modbus_devices:
            mb_device = convert_obj_to_dict(modbus_device)
            mb_device["site"] = ahe_sys.models.Site.objects.get(id=site_id)
            mb_device["map"] = ahe_mb.models.Map.objects.get(
                name=mb_device["map"])
            mb_device = ahe_mb.models.ModbusDevice.objects.create(**mb_device)
            mb_device = convert_obj_to_dict(mb_device)
            mb_devices.append(mb_device)
        return {"modbus_devices": mb_devices}
    except Exception as e:
        print(e)


class DownloadModbusMap:

    def create_modbus_field(self, modbus_fields):
        try:

            ahe_mb.models.Field.objects.bulk_create(
                modbus_fields, ignore_conflicts=True)
            print("bulk insert")
        except Exception:
            print("individual insert")
            for modbus_field in modbus_fields:
                modbus_field.save()

    def download_modbus_map(self, data):
        if data.get("map"):
            modbus_map = ahe_mb.models.Map.objects.get_or_create(
                name=data["map"])
            modbus_map = modbus_map[0]
            modbus_fields = []
            response = requests.get(MODBUS_SERVER_URL, params={
                "maps": modbus_map.name})
            for data in response.json():
                data["map"] = modbus_map
                modbus_fields.append(ahe_mb.models.Field(**data))
            self.create_modbus_field(modbus_fields)


def add_modbus_device_events(data):
    modbus_events = []
    for d in data:
        for device in ahe_mb.models.ModbusDevice.objects.filter(map=d["map"]):
            d["map"] = ahe_mb.models.Map.objects.get(name=d["map"])
            d["device"] = device
            modbus_events.append(ahe_mb.models.ModbusMapEvents(**d))
    ahe_mb.models.ModbusMapEvents.objects.bulk_create(
        modbus_events, ignore_conflicts=True)
