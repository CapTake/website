# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-11-26 20:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0024_auto_20171126_2030'),
    ]

    operations = [
        migrations.AddField(
            model_name='cryptocurrency',
            name='max_supply',
            field=models.DecimalField(decimal_places=8, default=0, max_digits=21),
        ),
    ]
