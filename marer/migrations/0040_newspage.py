# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-17 21:18
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models
import marer.models.base


class Migration(migrations.Migration):

    dependencies = [
        ('marer', '0039_fix_issue_issuer_registration_date_field_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('published_at', models.DateTimeField(verbose_name='news publish date and time')),
                ('picture', models.ImageField(blank=True, null=True, upload_to=marer.models.base.news_pictures_upload_path, verbose_name='news picture')),
                ('name', models.CharField(max_length=512, verbose_name='news name')),
                ('_seo_h1', models.CharField(blank=True, default='', max_length=512, verbose_name='name on page')),
                ('_seo_title', models.CharField(blank=True, default='', max_length=512, verbose_name='browser title')),
                ('_seo_description', models.CharField(blank=True, default='', max_length=512, verbose_name='page desctiption')),
                ('_seo_keywords', models.CharField(blank=True, default='', max_length=512, verbose_name='page keywords')),
                ('page_content', ckeditor.fields.RichTextField(blank=True, default='', verbose_name='news content')),
            ],
            options={
                'verbose_name': 'news page',
                'ordering': ['-published_at'],
                'verbose_name_plural': 'news pages',
            },
        ),
    ]