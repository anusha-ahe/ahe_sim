# Generated by Django 5.0.2 on 2024-05-27 21:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_mb', '0023_alter_sitedevice_site_device_conf_and_more'),
        ('ahe_sim', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='input',
            name='device',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ahe_mb.sitedevice'),
        ),
        migrations.AddField(
            model_name='output',
            name='device',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='ahe_mb.sitedevice'),
        ),
    ]
