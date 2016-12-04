# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sptf_user',
            name='refresh_token',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='sptf_user',
            name='token',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='sptf_user',
            name='sptf_username',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
