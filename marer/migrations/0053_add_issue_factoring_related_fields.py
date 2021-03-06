# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-14 11:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0052_user_is_broker'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='factoring_avg_actual_buyers_payment_term',
            field=models.IntegerField(blank=True, null=True, verbose_name='Срок лизинга (мес.)'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_manufactured_goods',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='виды производимых товаров'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_max_contract_deferred_payment_term',
            field=models.IntegerField(blank=True, null=True, verbose_name='Срок лизинга (мес.)'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_closed',
            field=models.NullBooleanField(verbose_name='закрытый факторинг'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_cred_risks_cover',
            field=models.NullBooleanField(verbose_name='покрытие кредитных рисков'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_export',
            field=models.NullBooleanField(verbose_name='экспортный факторинг'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_import',
            field=models.NullBooleanField(verbose_name='импортный факторинг'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_not_regressive',
            field=models.NullBooleanField(verbose_name='факторинг без регресса'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_orders_financing',
            field=models.NullBooleanField(verbose_name='финансирование заказов'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_regressive',
            field=models.NullBooleanField(verbose_name='регрессивный факторинг'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_product_is_suppliers_financing',
            field=models.NullBooleanField(verbose_name='финансирование поставщиков'),
        ),
        migrations.AddField(
            model_name='issue',
            name='factoring_sale_goods_or_services',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='виды реализуемых товаров/услуг'),
        ),
    ]
