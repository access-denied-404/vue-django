# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-01 19:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0048_financeorgproductproposedocument'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financeorgproductconditions',
            name='credit_interest_rate',
        ),
        migrations.RemoveField(
            model_name='financeorgproductconditions',
            name='credit_max_sum',
        ),
        migrations.RemoveField(
            model_name='financeorgproductconditions',
            name='credit_min_sum',
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_contract_exec_interest_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по кредиту на исполнение контракта'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_contract_exec_issue_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по кредиту на исполнение контракта'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_contract_exec_max_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_contract_exec_min_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_overdraft_interest_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по овердрафту'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_overdraft_issue_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по овердрафту'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_overdraft_max_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_overdraft_min_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_project_financing_interest_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по проектному финансированию'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_project_financing_issue_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по проектному финансированию'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_project_financing_max_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_project_financing_min_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_renewable_credit_line_interest_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по ВКЛ'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_renewable_credit_line_issue_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по ВКЛ'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_renewable_credit_line_max_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_renewable_credit_line_min_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_tender_interest_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по тендерному кредиту'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_tender_issue_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по тендерному кредиту'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_tender_max_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_tender_min_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_work_capital_refill_interest_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по кредиту на пополнение оборотных средств'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_work_capital_refill_issue_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='Годовая ставка по кредиту на пополнение оборотных средств'),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_work_capital_refill_max_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='financeorgproductconditions',
            name='credit_work_capital_refill_min_sum',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]