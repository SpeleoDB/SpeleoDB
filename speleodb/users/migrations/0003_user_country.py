# Generated by Django 5.0.6 on 2024-06-03 03:40

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='country',
            field=django_countries.fields.CountryField(default='MX', max_length=2),
            preserve_default=False,
        ),
    ]
