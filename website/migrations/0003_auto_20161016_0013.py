# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-10-16 04:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='rating_dislikes',
            field=models.PositiveIntegerField(blank=True, default=0, editable=False),
        ),
        migrations.AddField(
            model_name='project',
            name='rating_likes',
            field=models.PositiveIntegerField(blank=True, default=0, editable=False),
        ),
    ]
