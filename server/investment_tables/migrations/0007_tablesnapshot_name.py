# Generated by Django 5.1.6 on 2025-02-23 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment_tables', '0006_tablesnapshotitem_coefficient_is_not_negative'),
    ]

    operations = [
        migrations.AddField(
            model_name='tablesnapshot',
            name='name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
