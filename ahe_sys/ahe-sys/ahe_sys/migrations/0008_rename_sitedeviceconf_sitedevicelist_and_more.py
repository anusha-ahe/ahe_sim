# Generated by Django 4.2.6 on 2023-11-28 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sys', '0007_sitedevice_version'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SiteDeviceConf',
            new_name='SiteDeviceList',
        ),
        migrations.RemoveField(
            model_name='sitedevice',
            name='version',
        ),
    ]
