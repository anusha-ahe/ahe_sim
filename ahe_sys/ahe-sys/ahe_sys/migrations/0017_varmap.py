# Generated by Django 5.0.1 on 2024-02-09 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sys', '0016_delete_keymap'),
    ]

    operations = [
        migrations.CreateModel(
            name='VarMap',
            fields=[
                ('var', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=5, unique=True)),
            ],
        ),
    ]
