# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-30 23:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gui', '0007_auto_20170730_2358'),
    ]

    operations = [
        migrations.RenameField(
            model_name='measurement',
            old_name='p_value',
            new_name='p_value_group_1_and_group_2',
        ),
    ]
