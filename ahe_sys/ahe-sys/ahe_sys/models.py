from email.policy import default
from unittest.util import _MAX_LENGTH
from django.db import models
from django.core.exceptions import ValidationError
import re


INTERFACE_TYPE = [('MODBUS', 'MODBUS'),
                  ('OPC', 'OPC')]

DEVICE_CATEGORY = [
    ("aircon", "Air conditioner"),
    ("aux", "Aux"),
    ("battery", "Battery"),
    ("co_sensor", "Co_sensor"),
    ("common_acdb", "Common acdb"),
    ("dc_meter", "DC meter"),
    ("ems", "Ems"),
    ("ess", "Ess"),
    ("grid", "Grid"),
    ("humidity", "Humidity sensor"),
    ("inverter", "Inverter"),
    ("load", "Load"),
    ("ppi_analog", "Ppi analog"),
    ("pv", "PV"),
    ("rack", "Rack"),
    ("temp_controller", "Temperature Controller"),
    ("temp_scanner", "Temperature Scanner"),
    ("bank", "bank"),
    ("cell", "Cell"),
    ("module", "Module"),
    ("string", "String"),
]

def is_valid_host_name(name):
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    match = allowed.match(name)
    return match


class Site(models.Model):
    id = models.IntegerField(primary_key=True)
    uuid = models.CharField(max_length=10, null=True, blank=True)
    name = models.CharField(max_length=50)
    client = models.ForeignKey('AheClient', on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        raise ValidationError("You can't delete a site")

    def __str__(self) -> str:
        return f'Site {self.id}:{self.name}'
    
    def save(self, *args, **kwargs):
        self.assign_site_id()
        self.full_clean()
        super(Site, self).save(*args, **kwargs)

    def assign_site_id(self):
        if not self.id:
            client = self.client
            print("assign_site_id", client, type(client))
            self.id = client.next_site_id


def convert_to_value(str):
    if str is None:
        return str
    if str == "True":
        return True
    if str == "False":
        return False
    if str.isdigit():
        return int(str)
    try:
        return float(str)
    except ValueError:
        return str

def get_site_metadata(site_id, meta, default=None):
    data  = read_metadata(site_id)
    return data.get(meta, default)

def read_metadata(site_id, site_meta_config=None, parent=None):
    print("called read_metadata", parent)
    data = dict()
    if not site_meta_config:
        max_version = SiteMetaConf.objects.filter(
            site=site_id).aggregate(models.Max('version'))["version__max"]
        print("max_version", max_version)
        config = SiteMetaConf.objects.filter(
            site=site_id, version=max_version).first()
    else:
        config = site_meta_config
    print("config", config)
    meta = SiteMeta.objects.filter(site_meta_conf=config, parent=parent)
    print("meta", meta)
    for m in meta:
        c_meta = read_metadata(site_id, site_meta_config, m.key)
        print("received c_meta", c_meta)
        if c_meta:
            data[m.key] = c_meta
        else:
            data[m.key] = convert_to_value(m.value)
    print("returning data", data)
    return data


class SiteMetaConf(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("You can't update a SiteMetaConf")
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You can't delete a SiteMetaConf")

    def __str__(self):
        return f"{self.site.name} Meta: V {self.version}"


class SiteMeta(models.Model):
    site_meta_conf = models.ForeignKey(
        SiteMetaConf, related_name='detail', on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=20, null=True, blank=True)
    parent = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ('site_meta_conf', 'key', "parent")

    def __str__(self):
        if self.parent:
            return f"{self.parent} - {self.key}"
        else:
            return f"{self.key}"


class SiteDeviceList(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("You can't update a SiteDeviceList")
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You can't delete a SiteDeviceList")

    def __str__(self):
        return f"{self.site.name} Dev: V {self.version}"


class DeviceType(models.Model):
    name = models.CharField(
        max_length=100)  # Trumph Inverter
    device_category = models.CharField(
        max_length=50, choices=DEVICE_CATEGORY)   # Inverter
    interface_type = models.CharField(
        max_length=25, choices=INTERFACE_TYPE, default="MODBUS")  # Modbus
    version = models.IntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.name} - {self.device_category} ({self.interface_type}) V{self.version}'


VARIABLE_CATEGORY = [
    ("Main", "Main"),
    ("Cell", "Cell"),
    ("Alarm", "Alarm"),
    ("Status", "Status"),
]


class SiteVariableList(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("You can't update a SiteVariableConf")
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You can't delete a SiteVariableConf")

    def __str__(self):
        return f"{self.site.name} Dev: V {self.version}"


class Variable(models.Model):
    site_variable_conf = models.ForeignKey(
        SiteVariableList, related_name='detail', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    med_name = models.CharField(max_length=100, default="")
    long_name = models.CharField(max_length=100, default="")
    require_in_frontend = models.BooleanField(default=False)
    measurement_unit = models.CharField(max_length=30, default="")
    decimal_places = models.IntegerField(default=2)
    category = models.CharField(
        max_length=30, choices=VARIABLE_CATEGORY, default="Main")
    device_type = models.ForeignKey(
        DeviceType, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.name}'


RULE_TYPE = [
    ("M", "Med Name"),
    ("L", "Long Name"),
    ("R", "Required in frontend"),
    ("D", "Decimal Places"),
    ("U", "Measurement Unit"),
]


class FieldRule(models.Model):
    rule_type = models.CharField(max_length=1, choices=RULE_TYPE)
    pattern = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


MODE_CHOICE = [
    ("A", "activePowerMode"),
    ("R", "reactivePowerMode"),
]


class AllowedMode(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    mode = models.CharField(max_length=100, choices=MODE_CHOICE)
    mode_id = models.IntegerField()
    name = models.CharField(max_length=30)


MODE_TYPE = [
    ("S", "slider"),
    ("T", "time"),
    ("H", "scheduler"),
    ("O", "select_options")
]


class ModeInput(models.Model):
    mode = models.ForeignKey(AllowedMode, on_delete=models.CASCADE)
    step = models.IntegerField()
    mode_type = models.CharField(max_length=100, choices=MODE_TYPE)
    unit = models.CharField(max_length=30)
    label = models.CharField(max_length=50)
    max_value = models.FloatField()
    min_value = models.FloatField()
    read_var_name = models.CharField(max_length=100)
    write_var_name = models.CharField(max_length=100)


class ModeInputOption(models.Model):
    mode_input = models.ForeignKey(ModeInput, on_delete=models.CASCADE)
    label = models.CharField(max_length=50)
    input = models.CharField(max_length=50)


class VarMap(models.Model):
    var = models.CharField(max_length=100, primary_key=True)
    key = models.CharField(max_length=5, unique=True)

    def __str__(self) -> str:
        return f'{self.key} --> {self.var}'
    
class AheClient(models.Model):
    name = models.CharField(max_length=50)
    start_site_id = models.IntegerField(default=0)
    end_site_id = models.IntegerField(default=0)

    def clean(self):
        if not is_valid_host_name(self.name):
            raise ValidationError({'name': "Invalid name"})
        super(AheClient, self).clean()

    def assign_site_id_range(self):
        if self.start_site_id != 0:
            return
        x = 1
        while True:
            x += 200
            sites = Site.objects.filter(id__gte=x, id__lt= x + 200).first()
            if sites:
               continue 
            clients = AheClient.objects.filter(start_site_id=x)
            if clients:
                continue
            self.start_site_id = x
            self.end_site_id = x + 199
            break

    def save(self, *args, **kwargs):
        self.assign_site_id_range()
        self.full_clean()
        super(AheClient, self).save(*args, **kwargs)

    @property
    def next_site_id(self):
        sites = Site.objects.filter(
            id__gte=self.start_site_id, id__lte=self.end_site_id).order_by("id")
        site_ids = [s.id for s in sites]
        for x in range(self.start_site_id, self.end_site_id):
            if x not in site_ids:
                return x

    def __str__(self) -> str:
        return f"AheClient: {self.name} ({self.start_site_id} - {self.end_site_id})"
    
