# Generated by Django 5.0 on 2023-12-22 03:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_mb', '0014_device_start_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceModifierConf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ahe_mb.device')),
            ],
        ),
        migrations.CreateModel(
            name='MapModifier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_spaces', models.BooleanField(default=False)),
                ('map_reg', models.CharField(choices=[('Coil', 'Coil'), ('Discrete Input', 'Discrete Input'), ('Input Register', 'Input Register'), ('Holding Register', 'Holding Register')], default='Holding Register', max_length=50)),
                ('map_max_read', models.IntegerField(default=120)),
                ('start_address', models.IntegerField(default=0)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ahe_mb.map')),
                ('mod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ahe_mb.devicemodifierconf')),
            ],
        ),
    ]
