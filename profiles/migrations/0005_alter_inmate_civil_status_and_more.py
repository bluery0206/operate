# Generated by Django 5.1.2 on 2024-11-02 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_alter_inmate_date_arrested_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inmate',
            name='civil_status',
            field=models.CharField(blank=True, choices=[('single', 'Single'), ('married', 'Married'), ('widowed', 'Widowed'), ('legally_separated', 'Legally Separated ')], default='civil_status', max_length=20),
        ),
        migrations.AlterField(
            model_name='personnel',
            name='civil_status',
            field=models.CharField(blank=True, choices=[('single', 'Single'), ('married', 'Married'), ('widowed', 'Widowed'), ('legally_separated', 'Legally Separated ')], default='civil_status', max_length=20),
        ),
    ]
