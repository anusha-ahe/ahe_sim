# Generated by Django 4.2.6 on 2023-11-29 04:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sys', '0012_delete_sitedevice'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SiteVariableConf',
            new_name='SiteVariableList',
        ),
    ]
