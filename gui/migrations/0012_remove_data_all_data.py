# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-16 18:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0011_auto_20170816_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data',
            name='all_data',
        ),
    ]
