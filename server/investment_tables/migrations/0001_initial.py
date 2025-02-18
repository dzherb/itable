# Generated by Django 5.1.6 on 2025-02-18 09:34

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exchange', '0001_initial'),
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TableTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TableSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table_snapshots', related_query_name='table_snapshot', to='portfolio.portfolio')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', related_query_name='snapshot', to='investment_tables.tabletemplate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TableTemplateItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('weight', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='template_items', related_query_name='template_item', to='exchange.security')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', related_query_name='item', to='investment_tables.tabletemplate')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='tabletemplate',
            name='securities',
            field=models.ManyToManyField(related_name='templates', related_query_name='template', through='investment_tables.TableTemplateItem', to='exchange.security'),
        ),
        migrations.CreateModel(
            name='TableSnapshotItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('snapshot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', related_query_name='item', to='investment_tables.tablesnapshot')),
                ('template_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshot_items', related_query_name='snapshot_item', to='investment_tables.tabletemplateitem')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='tablesnapshot',
            name='template_items',
            field=models.ManyToManyField(related_name='snapshots', related_query_name='snapshot', through='investment_tables.TableSnapshotItem', to='investment_tables.tabletemplateitem'),
        ),
    ]
