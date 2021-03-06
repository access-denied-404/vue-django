# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-26 17:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0017_issuefinanceorgproposeclarificationmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueFinanceOrgProposeClarificationMessageDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=512)),
                ('clarification_message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents_links', to='marer.IssueFinanceOrgProposeClarificationMessage')),
                ('document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clarification_messages_links', to='marer.Document')),
            ],
        ),
    ]
