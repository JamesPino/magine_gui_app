# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-30 22:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0004_auto_20170729_2213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='data',
            name='file_name_path',
        ),
    ]
