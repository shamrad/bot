# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-13 07:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='meaning',
            field=models.CharField(max_length=1231312312312312313, null=True),
        ),
    ]