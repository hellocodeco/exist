# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150921_1605'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='float_value',
            new_name='value',
        ),
    ]
