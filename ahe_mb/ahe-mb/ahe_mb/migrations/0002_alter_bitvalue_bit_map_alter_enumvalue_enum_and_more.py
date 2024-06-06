# Generated by Django 4.2.6 on 2023-11-23 11:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_mb', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bitvalue',
            name='bit_map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bit', to='ahe_mb.bitmap'),
        ),
        migrations.AlterField(
            model_name='enumvalue',
            name='enum',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='ahe_mb.enum'),
        ),
        migrations.AlterField(
            model_name='field',
            name='description',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='field',
            name='map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='ahe_mb.map'),
        ),
    ]