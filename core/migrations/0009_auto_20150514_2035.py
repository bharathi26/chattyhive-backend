# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150514_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='chrules',
            name='name',
            field=models.CharField(max_length=150, default='', unique=True),
            preserve_default=True,
        ),
    ]
