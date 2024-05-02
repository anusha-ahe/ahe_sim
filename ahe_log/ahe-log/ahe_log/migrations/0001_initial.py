# Generated by Django 4.2.6 on 2023-10-25 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EsLogger',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('logger_name', models.CharField(max_length=100)),
                ('level', models.CharField(choices=[('INFO', 'INFO'), ('WARNING', 'WARNING'), ('DEBUG', 'DEBUG'), ('ERROR', 'ERROR'), ('FATAL', 'FATAL')], max_length=50)),
                ('msg', models.TextField()),
                ('trace', models.TextField(blank=True, null=True)),
                ('file_name', models.CharField(blank=True, max_length=100, null=True)),
                ('line_no', models.IntegerField()),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
            ],
            options={
                'verbose_name': 'Logging',
                'verbose_name_plural': 'Logging',
                'db_table': 'es_logger',
                'ordering': ('-create_datetime',),
            },
        ),
    ]
