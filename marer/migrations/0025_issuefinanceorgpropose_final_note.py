# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-06 10:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0024_issuefinanceorgpropose_formalize_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuefinanceorgpropose',
            name='final_note',
            field=models.TextField(blank=True, default=''),
        ),
    ]