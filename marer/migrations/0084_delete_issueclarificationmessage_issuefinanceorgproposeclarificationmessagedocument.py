# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-23 10:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0083_issuerlicences'),
    ]

    operations = [
        migrations.DeleteModel(
            name='IssueClarificationMessage',
        ),
        migrations.DeleteModel(
            name='IssueFinanceOrgProposeClarificationMessageDocument',
        ),
    ]