from ahe_sys.models import DeviceType
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.http import JsonResponse
import ahe_sys
from rest_framework import status, viewsets, mixins
from ahe_mb.models import Field, Map, BitMap, BitValue, Enum, EnumValue, DeviceMap, SiteDevice
from ahe_sys.models import DeviceType, SiteDeviceList
from ahe_mb import DownloadModbusMap, add_modbus_device_events
from ahe_mb.serializer import  MapSerializer, MapListSerializer, ModbusCsvSerializer, \
    BitMapSerializer, BitMapListSerializer, BitMapCsvSerializer, \
    EnumSerializer, EnumListSerializer, EnumCsvSerializer, \
    SiteDevicesListSerializer, DeviceTypeSerializer, DeviceMapCsvSerializer, \
    SiteDeviceListSerializer, SiteDeviceConfCsvSerializer
from ahe_sys.serializer import DeviceTypeListSerializer
from django.db.models import Max
from rest_framework.response import Response
from rest_framework import status
import io
import csv
from ahe_mb.form import UploadFileForm, UploadBitmapForm, UploadEnumForm, UploadDeviceMap
from django.views.decorators.csrf import csrf_exempt
from ahe_mb.loader import BitMapLoader, ModbusLoader, EnumLoader, DeviceMapLoader, SiteDeviceLoader
from ahe_sys.common.views import MasterDetailViewSet


def get_csv_response(file_name, fields, data):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    writer = csv.DictWriter(response, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)
    return response


def home_page(request):
    return render(request, "home-page.html")


def process_upload(master_loader, request, title):
    redirect = True
    # title = "Device Map"
    context = {"form": UploadFileForm(), 'name': title}
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # name = form.cleaned_data.get("name")
            map_file = form.cleaned_data.get("file")
            map_file = io.TextIOWrapper(map_file)
            data = list(csv.DictReader(map_file))
            response = master_loader.load_csv(data)
            if form.cleaned_data.get("redirect") != 'Y':
                redirect = False
            if not response:
                context["success"] = True
            context["response"] = response
        else:
            context["response"] = form.errors
        if redirect:
            return render(request, 'upload-form.html', context)
        else:
            status_code = 400 if response else 200
            return JsonResponse({"data": response}, status=status_code)
    else:
        return render(request, 'upload-form.html', context)

@csrf_exempt
def upload_modbus(request):
    loader = ModbusLoader()
    return process_upload(loader, request, "Modbus Map")


@csrf_exempt
def upload_bitmap(request):
    loader = BitMapLoader()
    return process_upload(loader, request, "Bitmap")


@csrf_exempt
def upload_enum(request):
    loader = EnumLoader()
    return process_upload(loader, request, "Upload Enum")


@csrf_exempt
def upload_device_map(request):
    loader = DeviceMapLoader()
    return process_upload(loader, request, "Device Map")

@csrf_exempt
def upload_site_device(request):
    loader = SiteDeviceLoader()
    return process_upload(loader, request, "Site Device")


def map_list_html(request):
    maps = Map.objects.all()
    context = {"maps": maps, "name": "Modbus", "url_prefix": "modbus"}
    return render(request, "list.html", context)


def bitmpap_list_html(request):
    bit_map = BitMap.objects.all()
    context = {"bit_maps": bit_map, "name": "BitMap", "url_prefix": "bitmap"}
    return render(request, "list.html", context)


def enum_list_html(request):
    enum = Enum.objects.all()
    context = {"enums": enum, "name": "Enum", "url_prefix": "enum"}
    return render(request, "list.html", context)

def device_map_list_html(request):
    enum = DeviceType.objects.all()
    context = {"devices": enum, "name": "Device", "url_prefix": "device"}
    return render(request, "list.html", context)


def site_device_list_html(request):
    site_devices = SiteDeviceList.objects.all()
    context = {"site_devices": site_devices, "name": "Site Device Conf"}
    return render(request, "list.html", context)


def bitmap_detail_html(request, id):
    bitmap = BitMap.objects.get(id=id)
    fields = BitValue.objects.filter(bit_map_id=bitmap)
    context = {"fields": fields, "map": bitmap, "name": "BitMap"}
    return render(request, "bitmap.html", context)


def map_detail_html(request, id):
    modbus_map = Map.objects.get(id=id)
    fields = Field.objects.filter(map=modbus_map)
    context = {"fields": fields, "map": modbus_map, "name": "Modbus"}
    return render(request, "modbus.html", context)


def enum_detail_html(request, id):
    enum = Enum.objects.get(id=id)
    fields = EnumValue.objects.filter(enum=enum)
    context = {"fields": fields, "map": enum, "name": "Enum"}
    return render(request, "enum.html", context)

def device_map_detail_html(request, id):
    master = DeviceType.objects.get(id=id)
    details = DeviceMap.objects.filter(device_type=master)
    context = {"details": details, "master": master, "name": "Device Map"}
    return render(request, "device-map.html", context)

def site_device_detail_html(request, id):
    master = SiteDeviceList.objects.get(id=id)
    details = SiteDevice.objects.filter(site_device_conf=master)
    context = {"details": details, "master": master, "name": "Site Device"}
    return render(request, "site-device.html", context)


def download_modbus_csv(request, id):
    modbus = Map.objects.get(id=id)
    fields = Field.objects.filter(map=modbus)
    serializer = ModbusCsvSerializer(fields, many=True)
    return get_csv_response(f"{str(modbus).replace(':','').replace(' ', '-')}.csv", serializer.data[0].keys(), serializer.data)


def download_bitmap_csv(request, id):
    bitmap = BitMap.objects.get(id=id)
    fields = BitValue.objects.filter(bit_map_id=bitmap)
    serializer = BitMapCsvSerializer(fields, many=True)
    return get_csv_response(f"{str(bitmap).replace(':','').replace(' ', '-')}.csv", serializer.data[0].keys(), serializer.data)


def download_enum_csv(request, id):
    enum = Enum.objects.get(id=id)
    fields = EnumValue.objects.filter(enum=enum)
    serializer = EnumCsvSerializer(fields, many=True)
    return get_csv_response(f"{str(enum).replace(':','').replace(' ', '-')}.csv", serializer.data[0].keys(), serializer.data)

def download_device_map_csv(request, id):
    master = DeviceType.objects.get(id=id)
    details = DeviceMap.objects.filter(device_type=master)
    serializer = DeviceMapCsvSerializer(details, many=True)
    return get_csv_response(f"{str(master).replace(':','').replace(' ', '-')}.csv", serializer.data[0].keys(), serializer.data)


def download_site_device_csv(request, id):
    master = SiteDeviceList.objects.get(id=id)
    details = SiteDevice.objects.filter(site_device_conf=master)
    serializer = SiteDeviceConfCsvSerializer(details, many=True)
    return get_csv_response(f"{str(master).replace(':','').replace(' ', '-')}.csv", serializer.data[0].keys(), serializer.data)


class BitMapViewSet(MasterDetailViewSet):
    master_serializer = BitMapSerializer
    list_serializer = BitMapListSerializer


class EnumViewSet(MasterDetailViewSet):
    master_serializer = EnumSerializer
    list_serializer = EnumListSerializer


class MapViewSet(MasterDetailViewSet):
    master_serializer = MapSerializer
    list_serializer = MapListSerializer

class SiteDevicesViewSet(MasterDetailViewSet):
    master_serializer = SiteDeviceListSerializer
    list_serializer = SiteDevicesListSerializer
    search_field = "site"

class DevicesMapViewSet(MasterDetailViewSet):
    master_serializer = DeviceTypeSerializer
    list_serializer = DeviceTypeListSerializer
 