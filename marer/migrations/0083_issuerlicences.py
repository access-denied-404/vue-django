# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-23 10:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0082_issueproposedocument_is_approved_by_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssuerLicences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, verbose_name='номер')),
                ('activity', models.TextField(max_length=1024, verbose_name='деятельность')),
                ('date_from', models.DateField(verbose_name='действительна с')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='действительна по')),
                ('active', models.BooleanField(default=True, verbose_name='активна')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issuer_licences', to='marer.Issue')),
            ],
        ),
    ]