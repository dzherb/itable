# Generated by Django 5.1.6 on 2025-03-11 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_itableuser_managers_remove_itableuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='itableuser',
            name='refresh_token',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
