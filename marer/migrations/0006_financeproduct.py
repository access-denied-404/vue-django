# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-18 11:08
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


def fill_finance_products(apps, schema_editor):
    finance_product_model = apps.get_model("marer", "FinanceProduct")
    finance_product_model(id=40, name='Банки и МФО', parent_id=None, lft=1, rght=32, tree_id=1, level=0).save()
    finance_product_model(id=1, name='Обеспечение госконтрактов', parent_id=40, lft=2, rght=9, tree_id=1, level=1).save()
    finance_product_model(id=7, name='Тендерный кредит', parent_id=1, lft=3, rght=4, tree_id=1, level=2).save()
    finance_product_model(id=10, name='Кредит на исполнение госконтракта', parent_id=1, lft=5, rght=6, tree_id=1, level=2).save()
    finance_product_model(id=41, name='Банковская гарантия', parent_id=1, lft=7, rght=8, tree_id=1, level=2).save()
    finance_product_model(id=2, name='Кредиты', parent_id=40, lft=10, rght=25, tree_id=1, level=1).save()
    finance_product_model(id=12, name='Овердрафт', parent_id=2, lft=11, rght=12, tree_id=1, level=2).save()
    finance_product_model(id=42, name='Кредитная линия', parent_id=2, lft=13, rght=14, tree_id=1, level=2).save()
    finance_product_model(id=15, name='Кредит на исполнение контракта', parent_id=2, lft=15, rght=16, tree_id=1, level=2).save()
    finance_product_model(id=16, name='Кредит на пополнение оборотных средств', parent_id=2, lft=17, rght=18, tree_id=1, level=2).save()
    finance_product_model(id=17, name='Мезонинное кредитование', parent_id=2, lft=19, rght=20, tree_id=1, level=2).save()
    finance_product_model(id=18, name='Синдицированное кредитование', parent_id=2, lft=21, rght=22, tree_id=1, level=2).save()
    finance_product_model(id=19, name='Проектное финансирвоание', parent_id=2, lft=23, rght=24, tree_id=1, level=2).save()
    finance_product_model(id=20, name='Рассчетно-кассовое обслуживание', parent_id=40, lft=26, rght=27, tree_id=1, level=1).save()
    finance_product_model(id=21, name='Зарплатные проекты', parent_id=40, lft=28, rght=29, tree_id=1, level=1).save()
    finance_product_model(id=22, name='Внешняя экономическая деятельность', parent_id=40, lft=30, rght=31, tree_id=1, level=1).save()
    finance_product_model(id=3, name='Лизинг', parent_id=None, lft=1, rght=8, tree_id=7, level=0).save()
    finance_product_model(id=23, name='Лизинг автотранспорта', parent_id=3, lft=2, rght=3, tree_id=7, level=1).save()
    finance_product_model(id=24, name='Лизинг оборудования', parent_id=3, lft=4, rght=5, tree_id=7, level=1).save()
    finance_product_model(id=25, name='Лизинг спецтехники', parent_id=3, lft=6, rght=7, tree_id=7, level=1).save()
    finance_product_model(id=4, name='Факторинг', parent_id=None, lft=1, rght=14, tree_id=8, level=0).save()
    finance_product_model(id=26, name='Классический факторинг', parent_id=4, lft=2, rght=3, tree_id=8, level=1).save()
    finance_product_model(id=27, name='Конфиденциальный факторинг', parent_id=4, lft=4, rght=5, tree_id=8, level=1).save()
    finance_product_model(id=28, name='Бездокументарный факторинг', parent_id=4, lft=6, rght=7, tree_id=8, level=1).save()
    finance_product_model(id=29, name='Безрегрессный факторинг', parent_id=4, lft=8, rght=9, tree_id=8, level=1).save()
    finance_product_model(id=30, name='Реверсивный факторинг', parent_id=4, lft=10, rght=11, tree_id=8, level=1).save()
    finance_product_model(id=31, name='Дополнительная отсрочка платежа дебитору', parent_id=4, lft=12, rght=13, tree_id=8, level=1).save()
    finance_product_model(id=5, name='Страхование', parent_id=None, lft=1, rght=14, tree_id=9, level=0).save()
    finance_product_model(id=32, name='Автокредитование', parent_id=5, lft=2, rght=3, tree_id=9, level=1).save()
    finance_product_model(id=33, name='Добровольное медицинское страхование', parent_id=5, lft=4, rght=5, tree_id=9, level=1).save()
    finance_product_model(id=34, name='Строймонтажные риски', parent_id=5, lft=6, rght=7, tree_id=9, level=1).save()
    finance_product_model(id=35, name='Страхование гражданской ответственности застройщика (214-ФЗ)', parent_id=5, lft=8, rght=9, tree_id=9, level=1).save()
    finance_product_model(id=36, name='Страхование грузов', parent_id=5, lft=10, rght=11, tree_id=9, level=1).save()
    finance_product_model(id=37, name='Страхование жизни', parent_id=5, lft=12, rght=13, tree_id=9, level=1).save()
    finance_product_model(id=6, name='Фонды', parent_id=None, lft=1, rght=6, tree_id=10, level=0).save()
    finance_product_model(id=38, name='Венчурные фонды', parent_id=6, lft=2, rght=3, tree_id=10, level=1).save()
    finance_product_model(id=39, name='Частные инвесторы', parent_id=6, lft=4, rght=5, tree_id=10, level=1).save()
    finance_product_model(id=43, name='Программы господдержки', parent_id=None, lft=1, rght=8, tree_id=11, level=0).save()
    finance_product_model(id=44, name='Муниципальные', parent_id=43, lft=2, rght=3, tree_id=11, level=1).save()
    finance_product_model(id=45, name='Областные', parent_id=43, lft=4, rght=5, tree_id=11, level=1).save()
    finance_product_model(id=46, name='Федеральные', parent_id=43, lft=6, rght=7, tree_id=11, level=1).save()


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0005_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinanceProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
                ('_seo_h1', models.CharField(blank=True, default='', max_length=512)),
                ('_seo_title', models.CharField(blank=True, default='', max_length=512)),
                ('_seo_description', models.CharField(blank=True, default='', max_length=512)),
                ('_seo_keywords', models.CharField(blank=True, default='', max_length=512)),
                ('page_content', ckeditor.fields.RichTextField(blank=True, default='')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='childrens', to='marer.FinanceProduct')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(fill_finance_products, migrations.RunPython.noop)
    ]
