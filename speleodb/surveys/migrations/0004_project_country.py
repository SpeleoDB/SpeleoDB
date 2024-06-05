# Generated by Django 5.0.6 on 2024-06-04 04:54

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_alter_project_latitude_alter_project_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='country',
            field=django_countries.fields.CountryField(default='MX', max_length=2),
            preserve_default=False,
        ),
    ]
