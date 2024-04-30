from django.contrib import admin

import ahe_mb
import ahe_sys

# @admin.register(ahe_mb.models.ModbusDevice)
# class DeviceAdmin(admin.ModelAdmin):
#     list_display = ['site', 'id', 'name',
#                     'map', 'ip_address', 'port', 'unit']
#     list_filter = ['site', 'map', 'ip_address', 'port', 'unit']
#     search_fields = ['name', 'map']


class FieldInline(admin.TabularInline):
    model = ahe_mb.models.Field


@admin.register(ahe_mb.models.Map)
class MapAdmin(admin.ModelAdmin):
    model = ahe_mb.models.Map
    inlines = (FieldInline, )
    list_display = ['name', 'version']
    search_fields = ['name']


class BitValueInline(admin.TabularInline):
    model = ahe_mb.models.BitValue


@admin.register(ahe_mb.models.BitMap)
class BitMapAdmin(admin.ModelAdmin):
    model = ahe_mb.models.BitMap
    inlines = (BitValueInline, )


class EnumValueInline(admin.TabularInline):
    model = ahe_mb.models.EnumValue


@admin.register(ahe_mb.models.Enum)
class EnumAdmin(admin.ModelAdmin):
    model = ahe_mb.models.Enum
    inlines = (EnumValueInline, )


class DeviceMapInline(admin.TabularInline):
    model = ahe_mb.models.DeviceMap


@admin.register(ahe_sys.models.DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    model = ahe_sys.models.DeviceType
    inlines = (DeviceMapInline, )
    list_filter = ['device_category', 'interface_type']
    search_fields = ['name']


class SiteDeviceInline(admin.TabularInline):
    model = ahe_mb.models.SiteDevice

@admin.register(ahe_mb.models.SiteDeviceList)
class SiteDeviceListAdmin(admin.ModelAdmin):
    model = ahe_mb.models.SiteDeviceList
    inlines = (SiteDeviceInline, )
    search_fields = ['name']

