# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-11-21 01:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_grant_corpus'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
