# Generated by Django 4.2.6 on 2023-11-17 07:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sys', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitedevice',
            name='site_device_conf',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_device', to='ahe_sys.sitedeviceconf'),
        ),
        migrations.AlterField(
            model_name='sitemeta',
            name='site_meta_conf',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_meta', to='ahe_sys.sitemetaconf'),
        ),
        migrations.AlterField(
            model_name='variable',
            name='site_device_conf',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_variable', to='ahe_sys.sitedeviceconf'),
        ),
    ]
