# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-23 06:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('democracy', '0006_remove-coords-add-geojson'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='plugin_data',
            field=models.TextField(blank=True, verbose_name='plugin data'),
        ),
        migrations.AddField(
            model_name='section',
            name='plugin_identifier',
            field=models.CharField(blank=True, max_length=255, verbose_name='plugin identifier'),
        ),
    ]