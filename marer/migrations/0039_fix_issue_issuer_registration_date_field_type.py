# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-17 20:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0038_add_custom_managers_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='issuer_registration_date',
            field=models.DateField(blank=True, null=True, verbose_name='дата рождения руководителя'),
        ),
    ]
