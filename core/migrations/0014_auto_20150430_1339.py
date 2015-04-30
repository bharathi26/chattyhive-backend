# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20150429_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='chhive',
            name='deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
