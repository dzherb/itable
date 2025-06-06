# Generated by Django 5.1.6 on 2025-02-18 09:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exchange', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PortfolioItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_items', related_query_name='portfolio_item', to='portfolios.portfolio')),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portfolio_items', related_query_name='portfolio_item', to='exchange.security')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='portfolio',
            name='securities',
            field=models.ManyToManyField(related_name='portfolios', related_query_name='portfolio', through='portfolios.PortfolioItem', to='exchange.security'),
        ),
    ]
