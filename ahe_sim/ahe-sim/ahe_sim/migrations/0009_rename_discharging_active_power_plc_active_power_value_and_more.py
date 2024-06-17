# Generated by Django 5.0.2 on 2024-06-13 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sim', '0008_plc_active_power_variable'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plc',
            old_name='discharging_active_power',
            new_name='active_power_value',
        ),
        migrations.RemoveField(
            model_name='plc',
            name='charging_active_power',
        ),
    ]
