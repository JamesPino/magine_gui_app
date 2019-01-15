# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-15 23:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('gui', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='measurements',
        ),
        migrations.RemoveField(
            model_name='genelist',
            name='gene_list',
        ),
        migrations.RemoveField(
            model_name='project',
            name='samples',
        ),
        migrations.DeleteModel(
            name='Dataset',
        ),
        migrations.DeleteModel(
            name='Gene',
        ),
        migrations.DeleteModel(
            name='GeneList',
        ),
        migrations.DeleteModel(
            name='Measurement',
        ),
        migrations.DeleteModel(
            name='Project',
        ),
    ]
