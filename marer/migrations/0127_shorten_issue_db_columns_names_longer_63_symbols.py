# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-04 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0126_set_tender_final_cost_to_0_by_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets',
            field=models.NullBooleanField(db_column='is_absent_info_about_court_acts_for_more_than_20_pct_of_net_as', verbose_name='Отсутствие информации об исполнительных производствах Приницпала его Участников на сумму более 20% чистых активов Клиента'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='is_absent_info_about_court_cases_on_ifns_or_bankrupts_or_contracts_as_defendant',
            field=models.NullBooleanField(db_column='is_absent_info_about_court_cases_on_ifns_or_bankrupts_or_contr', verbose_name='Отсутствие наличия информации о судебных разбирательствах по искам, ответчиком по которым является Принципал: по судебным разбирательствам с ИФНС, по заявлениям о признании Принципала несостоятельным (банкротом), по искам неисполнения государственных контрактов'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets',
            field=models.NullBooleanField(db_column='is_absent_info_about_legal_proceedings_as_defendant_for_more_t', verbose_name='Отсутствие информации о судебных разбирательствах Клиента в качестве ответчика (за исключением закрытых) на сумму более 30% чистых активов Клиента'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='is_absent_info_about_prev_convictions_on_issuer_head_or_shareholders_or_participants_or_guarantor',
            field=models.NullBooleanField(db_column='is_absent_info_about_prev_convictions_on_issuer_head_or_shareh', verbose_name='Отсутствие судимостей в отношении физических лиц (генеральный директор, участники юридического лица (c наибольшей долей участия, Поручитель)'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='is_contract_price_reduction_lower_than_50_pct_on_supply_contract',
            field=models.NullBooleanField(db_column='is_contract_price_reduction_lower_than_50_pct_on_supply_contra', verbose_name='Снижение цены Контракта менее 50% если предмет контракта «Поставка»'),
        ),
    ]