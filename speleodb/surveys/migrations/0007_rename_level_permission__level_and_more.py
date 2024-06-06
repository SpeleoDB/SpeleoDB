# Generated by Django 5.0.6 on 2024-06-06 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0006_project_software'),
    ]

    operations = [
        migrations.RenameField(
            model_name='permission',
            old_name='level',
            new_name='_level',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='software',
            new_name='_software',
        ),
        migrations.AddField(
            model_name='project',
            name='_visibility',
            field=models.IntegerField(choices=[(0, 'PRIVATE'), (1, 'PUBLIC')], default=0, verbose_name='visibility'),
        ),
    ]
