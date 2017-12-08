# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-08 15:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0067_add_region_classification_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1100_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1100_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1200_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1200_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1400_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1400_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1500_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1500_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1700_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_1700_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2100_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2100_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2200_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2200_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2300_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2300_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2500_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2500_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2900_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2900_offset_1',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2910_offset_0',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='balance_code_2910_offset_1',
        ),
        migrations.AddField(
            model_name='issue',
            name='balance_code_2110_offset_0',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='balance_code_2110_offset_1',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
