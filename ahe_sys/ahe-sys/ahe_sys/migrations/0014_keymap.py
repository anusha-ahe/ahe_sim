# Generated by Django 5.0.1 on 2024-01-04 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sys', '0013_rename_sitevariableconf_sitevariablelist'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeyMap',
            fields=[
                ('var', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=10, unique=True)),
            ],
        ),
    ]
