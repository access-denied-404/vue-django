# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-28 11:41
from __future__ import unicode_literals

from django.db import migrations, models



class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0088_issue_tax_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='financeorgproductproposedocument',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'Юридические документы'), (2, 'Финансовые документы'), (3, 'Прочее')], default=3),
        ),
        migrations.AddField(
            model_name='issueproposedocument',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'Юридические документы'), (2, 'Финансовые документы'), (3, 'Прочее')], default=3),
        ),
    ]
