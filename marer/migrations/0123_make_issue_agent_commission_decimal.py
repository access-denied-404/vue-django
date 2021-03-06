# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-28 06:52
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


def create_missing_contacts(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    issue = apps.get_model('marer', 'Issue')
    issues = issue.objects.using(db_alias).exclude(agent_comission__isnull=True).exclude(agent_comission='')
    for issue in issues:
        ac = str(issue.agent_comission)
        ac = ac.replace(' ', '')
        ac = ac.replace(',', '.')
        ac = Decimal(ac)
        issue.agent_comission = ac
        issue.save()


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0122_approval_and_change_sheet'),
    ]

    operations = [
        migrations.RunPython(create_missing_contacts, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='issue',
            name='agent_comission',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=32, verbose_name='Комиссия агента'),
        ),
    ]
