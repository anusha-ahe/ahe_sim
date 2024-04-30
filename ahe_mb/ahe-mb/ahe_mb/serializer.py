from ahe_mb.models import Field, Map, BitValue, EnumValue, BitMap, Enum, SiteDevice, DeviceMap
from ahe_sys.models import DeviceType, SiteDeviceList
from rest_framework import serializers
from ahe_common.serializers import MasterSerializer, DetailSerializer, is_valid_name, FIELD_INVALID_VALUE
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel
from rest_framework.exceptions import ValidationError



# BITMAP_COLUMNS = [f.name for f in BitMap._meta.get_fields() if type(f) not in (ManyToOneRel, ManyToManyRel) and f.name != "id"]
# BITMAP_COLUMNS = ["bit_map", "ahe_name", "start_bit", "end_bit", "description"]

def is_address_overlaping(a1, a2):
    if a1[0] < a2[0]:
        p1 = a1
        p2 = a2
    else:
        p2 = a1
        p1 = a2
    if p1[1] >= p2[0]:
        return True
    return False


class EnumCsvSerializer(serializers.ModelSerializer):
    enum = serializers.CharField(source='enum.name')

    class Meta:
        model = EnumValue
        fields = ["enum", "ahe_name",
                  "value", "description"]


class ModbusCsvSerializer(serializers.ModelSerializer):
    bit_map = serializers.SerializerMethodField()
    modbus_map = serializers.ReadOnlyField(source='map.name')

    def get_bit_map(self, obj):
        if obj.bit_map:
            return obj.bit_map.name
        else:
            return None

    class Meta:
        model = Field
        fields = ["modbus_map", "ahe_name", "description",
                  "field_address", "field_encoding", "field_format",
                  "field_scale", "field_offset", "field_size", "min_value",
                  "max_value", "bit_map", "enum", "measure_unit"]


class BitMapCsvSerializer(serializers.ModelSerializer):
    bit_map = serializers.CharField(source='bit_map.name')

    class Meta:
        model = BitValue
        fields = ["bit_map", "ahe_name",
                  "start_bit", "end_bit", "description"]


class BitSerializer(DetailSerializer):
    def prevalidate_ahe_name(self, value):
        if not is_valid_name(value):
            raise ValidationError(detail = {"ahe_name":[f"Invalid value {value}."]})
        return value

    def validate_start_bit(self, value):
        if int(value) < 0 or int(value) > 15:
            raise ValidationError(detail = [f"Invalid value {value}."])
        return value

    def validate_end_bit(self, value):
        if int(value) < 0 or int(value) > 15:
            raise ValidationError(detail = [f"Invalid value {value}."])
        return value

    def row_validation(self, row):
        if row["start_bit"] > row["end_bit"]:
            raise ValidationError(detail = {"end_bit":[f"Should not be less than start bit."]})
        return row


    class Meta:
        model = BitValue
        fields = ['ahe_name', 'start_bit', 'end_bit', 'description']
        master_column = "bit_map"


class BitMapListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitMap
        fields = '__all__'


class BitMapSerializer(MasterSerializer):
    detail = BitSerializer(many=True)

    def prevalidate_name(self, value):
        if not is_valid_name(value):
            raise ValidationError({"detail": [{"bit_map":[f"Invalid value {value}."]}]})
        return value


    def detail_validation(self, data):
        errors = []
        names_used = list()
        for row in data:
            print("names_used", names_used)
            if row["ahe_name"] in names_used:
                errors.append({"ahe_name":[f"{row['ahe_name']} already used."]})
            names_used.append(row["ahe_name"])
        ranges  = list()
        for row in data:
            range  = (row["start_bit"], row["end_bit"])
            for r in ranges:
                if is_address_overlaping(r, range):
                        errors.append({"end_bit":[f"Overlapping values {r}."]})
            ranges.append(range)
        if errors:
            raise ValidationError({"detail": errors})
        return data

    class Meta:
        model = BitMap
        fields = ['id', 'name', 'version', 'detail']
        detail_column = 'detail'


class ValueSerializer(DetailSerializer):

    class Meta:
        model = EnumValue
        fields = ['ahe_name', 'value', 'description']
        master_column = 'enum'


class EnumListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enum
        fields = '__all__'


class EnumSerializer(MasterSerializer):
    detail = ValueSerializer(many=True)

    class Meta:
        model = Enum
        fields = ['id', 'name', 'version', 'detail']
        detail_column = 'detail'


class FieldSerializer(DetailSerializer):
    bit_map = serializers.CharField(
        source='bit_map.name', required=False, allow_null=True)
    enum = serializers.CharField(
        source='enum.name', required=False, allow_null=True)

    def prevalidate_bit_map(self, value):
        if value == "":
            return None
        return value
    
    class Meta:
        model = Field
        fields = ['ahe_name', 'description', 'field_address', 'field_encoding', 'field_format', 'field_scale',
                  'field_offset', 'field_size', 'measure_unit', 'min_value', 'max_value', 'bit_map', 'enum']
        master_column = 'map'
        fk_cols = {'bit_map': 'name', 'enum': 'name'}


class MapListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'


class MapSerializer(MasterSerializer):
    detail = FieldSerializer(many=True)

    class Meta:
        model = Map
        fields = ['id', 'name', 'version', 'detail']
        detail_column = 'detail'


class SiteDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteDevice
        fields = ['id', 'name', 'device_type', 'ip_address',
                  'port', 'unit', 'data_hold_period']


class SiteDeviceListSerializer(MasterSerializer):
    detail = SiteDeviceSerializer(many=True)

    class Meta:
        model = SiteDeviceList
        fields = ['id', 'site', 'detail', 'version']


class SiteDevicesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteDeviceList
        fields = '__all__'


class SiteDeviceConfCsvSerializer(serializers.ModelSerializer):
    device_type = serializers.ReadOnlyField(source='device_type.name')
    site = serializers.CharField(source='site_device_conf.site.id')

    class Meta:
        model = SiteDevice
        fields = ['site', 'name', 'device_type',
                  'ip_address', 'port', 'unit', 'data_hold_period']


class DeviceTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'


class DeviceMapSerializer(DetailSerializer):
    map = serializers.CharField(source='map.name')

    class Meta:
        model = DeviceMap
        fields = ['map', 'read_spaces', 'map_reg',
                  'map_max_read', 'start_address']
        master_column = "device_type"
        fk_cols = {"map": "name"}


class DeviceTypeSerializer(MasterSerializer):
    detail = DeviceMapSerializer(many=True)

    class Meta:
        model = DeviceType
        fields = ['id', 'name', 'version',
                  'device_category', 'interface_type', 'detail']
        detail_column = 'detail'


class DeviceMapCsvSerializer(serializers.ModelSerializer):
    map = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField(source='device_type.name')
    device_category = serializers.ReadOnlyField(
        source='device_type.device_category')
    interface_type = serializers.ReadOnlyField(
        source='device_type.interface_type')

    def get_map(self, obj):
        if obj.map:
            return obj.map.name
        else:
            return None

    class Meta:
        model = DeviceMap
        fields = ["name", "device_category", "interface_type", "map",
                  "map_reg", "map_max_read", "read_spaces", "start_address"]
