# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-11 18:18
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20160611_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='instructors',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), default=[], size=None),
        ),
    ]