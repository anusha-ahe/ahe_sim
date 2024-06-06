# Generated by Django 4.2.6 on 2023-11-28 18:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sys', '0011_alter_sitedevice_site_device'),
        ('ahe_mb', '0004_alter_field_ahe_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='device_type',
        ),
        migrations.CreateModel(
            name='DeviceMap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ahe_sys.devicetype')),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ahe_mb.map')),
            ],
        ),
        migrations.CreateModel(
            name='DeviceConf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(max_length=50)),
                ('ip_address', models.CharField(max_length=20)),
                ('port', models.IntegerField()),
                ('unit', models.IntegerField()),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ahe_sys.devicetype')),
                ('site_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_device', to='ahe_sys.sitedevicelist')),
            ],
        ),
    ]