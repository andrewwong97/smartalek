# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-05 22:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20160605_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='Number',
            field=models.CharField(max_length=10),
        ),
    ]
