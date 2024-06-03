from django.db import models
from ahe_sys.models import Site, DeviceType, SiteDeviceList
from django.core.exceptions import ValidationError

# Create your models here.

REGISTER_TYPES = [('Coil', 'Coil'),
                  ('Discrete Input', 'Discrete Input'),
                  ('Input Register', 'Input Register'),
                  ('Holding Register', 'Holding Register')]


class Map(models.Model):
    name = models.CharField(max_length=200)
    version = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("You can't update a Map")
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You can't delete a Map")

    def __str__(self) -> str:
        return f'{self.name} V:{self.version}'
    
    def get_var_names(self, prefix):
        var_names = list()
        for field in self.detail.all():
            var_names.extend(field.get_var_names(prefix))
        return var_names


class DeviceMap(models.Model):
    device_type = models.ForeignKey(DeviceType, related_name='detail', on_delete=models.CASCADE)
    map = models.ForeignKey(Map, on_delete=models.CASCADE)
    read_spaces = models.BooleanField(default=False)
    map_reg = models.CharField(
        max_length=50, choices=REGISTER_TYPES, default='Holding Register')
    map_max_read = models.IntegerField(default=120)
    start_address = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'Dev: {self.device_type} Map:{self.map} @{self.start_address}'

    def get_var_names(self, prefix):
        return self.map.get_var_names(prefix)


FORMATS = [('bitmap', 'bitmap'),
           ('boolean', 'boolean'),
           ('string', 'string'),
           ('array', 'array'),
           ('uint16', 'uint16'),
           ('sint16', 'sint16'),
           ('uint32', 'uint32'),
           ('sint32', 'sint32'),
           ('float32', 'float32'), ]

ENCODINGS = [('', ''),
             ('Big-endian', 'Big-endian'),
             ('Little-endian', 'Little-endian'),
             ('Big-endian byte swap', 'Big-endian byte swap'),
             ('Little-endian byte swap', 'Little-endian byte swap'), ]




class SiteDevice(models.Model):
    site_device_conf = models.ForeignKey(
        SiteDeviceList, related_name='detail', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    device_type = models.ForeignKey(DeviceType, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=20)
    port = models.IntegerField()
    unit = models.IntegerField()
    data_hold_period = models.IntegerField(default=60)

    def __str__(self) -> str:
        return f'MB Device: {self.name} ({self.ip_address}:{self.port} Unit:{self.unit})'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_variables()

    def generate_variables(self):
        variables = []
        maps = self.device_type.detail.all()
        for map in maps:
            fields = map.map.detail.all()
            for field in fields:
                print(f"{self.name}_{field.ahe_name}")

    def get_var_names(self):
        var_names = list()
        maps = self.device_type.detail.all()
        for map in maps:
            var_names.extend(map.get_var_names(self.name))
        return var_names


class BitMap(models.Model):
    name = models.CharField(max_length=50)
    version = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("You can't update a BitMap")
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You can't delete a BitMap")

    def __str__(self) -> str:
        return f'{self.name} V:{self.version}'

    def get_var_names(self, prefix):
        var_names = list()
        for bit_value in self.detail.all():
            var_names.append(f"{prefix}_{bit_value.ahe_name}")
        return var_names


class BitValue(models.Model):
    bit_map = models.ForeignKey(
        BitMap, on_delete=models.CASCADE,  related_name='detail')
    ahe_name = models.CharField(max_length=250)
    start_bit = models.IntegerField()
    end_bit = models.IntegerField()
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        unique_together = (('bit_map', 'ahe_name'),)
        ordering = ('bit_map', 'start_bit')


    def __str__(self) -> str:
        return f'{self.bit_map.name}: {self.ahe_name} ({self.start_bit}-{self.end_bit})'


class Enum(models.Model):
    name = models.CharField(max_length=50)
    version = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("You can't update a Enum")
        else:
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("You can't delete a Enum")

    def __str__(self) -> str:
        return f'Enum:{self.name} V:{self.version}'


class EnumValue(models.Model):
    enum = models.ForeignKey(
        Enum, on_delete=models.CASCADE,  related_name='detail')
    ahe_name = models.CharField(max_length=250)
    value = models.IntegerField()
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        unique_together = (('enum', 'ahe_name'),)
        ordering = ('enum', 'value')

    def __str__(self) -> str:
        return f'{self.enum.name}_{self.ahe_name}'


class Field(models.Model):
    map = models.ForeignKey(
        Map, on_delete=models.CASCADE, related_name='detail')
    ahe_name = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, default="", null=True, blank=True)
    field_address = models.IntegerField()
    field_encoding = models.CharField(
        max_length=30, default='', choices=ENCODINGS)
    field_format = models.CharField(max_length=20, choices=FORMATS)
    field_scale = models.FloatField(default=1)
    field_offset = models.FloatField(default=0)
    field_size = models.IntegerField(default=0)
    measure_unit = models.CharField(max_length=50, blank=True, null=True)
    min_value = models.FloatField(blank=True, null=True)
    max_value = models.FloatField(blank=True, null=True)
    bit_map = models.ForeignKey(
        BitMap, on_delete=models.DO_NOTHING, blank=True, null=True)
    enum = models.ForeignKey(
        Enum, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self) -> str:
        if self.field_format in ('unt16', 'sint16', 'bitmap', 'boolean'):
            return f'Field:{self.ahe_name}-{self.field_format} size:1 @{self.field_address}'
        elif self.field_format in ('uint32', 'sint32', 'float32'):
            return f'Field:{self.ahe_name}-{self.field_format} size:2 @{self.field_address}'
        elif self.field_format not in ('string', 'array'):
            return f'Field:{self.ahe_name}-{self.field_format} @{self.field_address}'
        return f'Field:{self.ahe_name}-{self.field_format} size:{self.field_size} @{self.field_address} '

    def save(self, *args, **kwargs):
        modbus_fields = Field.objects.filter(map=self.map)
        for modbus_field in modbus_fields:
            for len in range(modbus_field.field_size):
                address = modbus_field.field_address + len
                if self.field_address == address:
                    raise ValueError(
                        f"field address {self.field_address} used multiple time for {self.map.name} map")
        super(Field, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('map', 'ahe_name', 'bit_map'),)
        ordering = ('map', 'field_address')


    def get_var_names(self, prefix):
        var_names = []
        if self.bit_map:
            bit_prefix = self.ahe_name.split("#")[0]
            var_names.extend(self.bit_map.get_var_names(f"{prefix}_{bit_prefix}"))
        else:
            var_names.append(f"{prefix}_{self.ahe_name}")
        return var_names