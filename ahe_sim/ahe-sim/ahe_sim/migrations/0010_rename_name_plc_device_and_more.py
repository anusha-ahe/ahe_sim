# Generated by Django 5.0.2 on 2024-06-16 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sim', '0009_rename_discharging_active_power_plc_active_power_value_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plc',
            old_name='name',
            new_name='device',
        ),
        migrations.RenameField(
            model_name='plc',
            old_name='active_power_value',
            new_name='value',
        ),
        migrations.RenameField(
            model_name='plc',
            old_name='active_power_variable',
            new_name='variable',
        ),
    ]
