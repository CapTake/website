# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-11-14 00:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_auto_20161103_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]