# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-13 07:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_auto_20170513_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='last_review',
            field=models.TimeField(null=True),
        ),
    ]
