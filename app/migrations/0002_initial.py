# Generated by Django 5.1.4 on 2024-12-22 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profiles_per_page', models.IntegerField(default=20)),
                ('thumbnail_size', models.IntegerField(default=200)),
                ('camera', models.IntegerField(default=0)),
                ('clip_camera', models.BooleanField(default=False)),
                ('clip_size', models.IntegerField(default=200)),
                ('threshold', models.FloatField(default=1.0)),
                ('input_size', models.IntegerField(default=105)),
                ('search_mode', models.CharField(choices=[('embedding', 'Embedding (Faster)'), ('image', 'Image')], default='embedding', max_length=9)),
                ('template_personnel', models.FileField(blank=True, null=True, upload_to='templates')),
                ('template_inmate', models.FileField(blank=True, null=True, upload_to='templates')),
                ('model', models.FileField(blank=True, null=True, upload_to='models')),
            ],
        ),
    ]
