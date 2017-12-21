# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-14 19:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0070_document_sign'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='sign_state',
            field=models.CharField(blank=True, choices=[('none', 'Отсутствует'), ('corrupted', 'Неверна'), ('verified', 'Проверена')], default='none', max_length=32),
        ),
    ]