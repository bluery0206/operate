# Generated by Django 5.1.4 on 2025-01-19 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_setting_model_recognition_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='setting',
            name='search_mode',
        ),
    ]
