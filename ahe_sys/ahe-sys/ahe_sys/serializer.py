from rest_framework import serializers
from ahe_common.serializers import MasterSerializer, DetailSerializer, IndependentSerializer
from ahe_sys.models import Site, DeviceType, SiteMeta, Variable, SiteMetaConf, \
    SiteVariableList, SiteMeta, AheClient
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel

# CLIENT_COLUMNS = [f.name for f in AheClient._meta.get_fields() if type(f) !=ManyToOneRel]
CLIENT_COLUMNS = ["id", "name", "start_site_id", "end_site_id"]
SITE_COLUMNS = [f.name for f in Site._meta.get_fields() if type(f) not in (ManyToOneRel, ManyToManyRel)]
DEVICE_TYPE_COLUMNS = ("name", "device_category", "interface_type")

class SiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Site
        fields = SITE_COLUMNS

class SiteCSVSerializer(serializers.ModelSerializer):
    client = serializers.ReadOnlyField(source='client.name')

    class Meta:
        model = Site
        fields = SITE_COLUMNS


class SiteMetaSerializer(DetailSerializer):
    class Meta:
        model = SiteMeta
        fields = ['key', 'value', 'parent']
        master_column = "site_meta_conf"
        # fk_cols = {"parent": "key"}

class SiteMetaConfSerializer(MasterSerializer):
    detail = SiteMetaSerializer(many=True)

    class Meta:
        model = SiteMetaConf
        fields = ['id', 'site', 'version', 'detail']
        detail_column = "detail"
        fk_cols = {"site": "id"}

class DeviceTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = '__all__'


# class SiteDeviceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SiteDevice
#         fields = ["device_name", "device_type"]


class VariableSerializer(DetailSerializer):
    class Meta:
        model = Variable
        fields = ["name"]
        master_column = "site_variable_conf"


class SiteVariableSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


# class SiteDeviceListSerializer(MasterSerializer):
#     site_device = SiteDeviceSerializer(many=True)
#     detail_model = SiteDevice
#     _related_name = "site_device"
#     _foraign_key_field = "site_device"

#     class Meta:
#         model = SiteDeviceList
#         fields = ['id', 'site', 'version', 'site_device']


class SiteVariableListSerializer(MasterSerializer):
    detail = VariableSerializer(many=True)
    # detail_model = Variable
    # _related_name = "site_variable"
    # _foraign_key_field = "site_variable_conf"

    class Meta:
        model = SiteVariableList
        fields = ['id', 'site', 'version', 'detail']
        detail_column = "detail"


class AheClientSerializer(IndependentSerializer):
    class Meta:
        model = AheClient
        fields = CLIENT_COLUMNS

    def validate_start_site_id(self, value):
        if value == 0:
            return value
        if self.instance and AheClient.objects.filter(start_site_id__lte=value, end_site_id__gte=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Start site id inside other client range')
        elif self.instance is None and AheClient.objects.filter(start_site_id__lte=value, end_site_id__gte=value).exists():        
            raise serializers.ValidationError('Start site id inside other client range')
        return value

    def validate_end_site_id(self, value):
        if value == 0:
            return value
        if self.instance and AheClient.objects.filter(start_site_id__lte=value, end_site_id__gte=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('End site id inside other client range')
        elif self.instance and AheClient.objects.filter(start_site_id__gte=self.instance.start_site_id, start_site_id__lte=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Other client inside this client range')
        elif self.instance and AheClient.objects.filter(end_site_id__gte=self.instance.start_site_id, end_site_id__lte=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Other client inside this client range')
        elif self.instance is None and AheClient.objects.filter(start_site_id__lte=value, end_site_id__gte=value).exists():
            raise serializers.ValidationError('End site id inside other client range')
        # add validate function
        # elif self.instance is None and AheClient.objects.filter(start_site_id__gte=self.instance.start_site_id, start_site_id__lte=value).exists():
        #     raise serializers.ValidationError('Other client inside this client range')
        # elif self.instance is None and AheClient.objects.filter(end_site_id__gte=self.instance.start_site_id, end_site_id__lte=value).exists():
        #     raise serializers.ValidationError('Other client inside this client range')
        return value

