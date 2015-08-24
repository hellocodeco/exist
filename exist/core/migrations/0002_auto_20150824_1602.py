# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='attribute_id',
        ),
        migrations.RemoveField(
            model_name='event',
            name='user_id',
        ),
        migrations.AddField(
            model_name='event',
            name='attribute',
            field=models.ForeignKey(default=1, related_name='events', to='core.Attribute'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(default=1, related_name='events', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
