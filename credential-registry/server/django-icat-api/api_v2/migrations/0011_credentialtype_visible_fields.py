# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-10 21:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v2', '0010_auto_20180907_2354'),
    ]

    operations = [
        migrations.AddField(
            model_name='credentialtype',
            name='visible_fields',
            field=models.TextField(null=True),
        ),
    ]
