# Generated by Django 5.1.4 on 2025-01-15 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_setting_clip_size'),
    ]

    operations = [
        migrations.RenameField(
            model_name='setting',
            old_name='model',
            new_name='model_detection',
        ),
        migrations.AddField(
            model_name='setting',
            name='model_recognition',
            field=models.FileField(blank=True, null=True, upload_to='models'),
        ),
    ]
