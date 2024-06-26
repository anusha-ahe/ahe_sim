# Generated by Django 4.2.6 on 2023-11-18 06:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sys', '0004_alter_sitemeta_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteVariableConf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField()),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ahe_sys.site')),
            ],
        ),
        migrations.AlterField(
            model_name='variable',
            name='site_device_conf',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_variable', to='ahe_sys.sitevariableconf'),
        ),
    ]
