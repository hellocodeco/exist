# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150824_1602'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='int_value',
        ),
        migrations.RemoveField(
            model_name='event',
            name='string_value',
        ),
        migrations.AlterField(
            model_name='event',
            name='float_value',
            field=models.DecimalField(null=True, blank=True, max_digits=16, decimal_places=4),
        ),
    ]
