# Generated by Django 5.0.2 on 2024-05-30 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ahe_sim', '0005_alter_input_variable'),
    ]

    operations = [
        migrations.AddField(
            model_name='testscenario',
            name='priority',
            field=models.IntegerField(default=1),
        ),
    ]