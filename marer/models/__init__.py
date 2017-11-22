from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import BooleanField
from django.utils.translation import ugettext_lazy as _
from mptt import models as mptt_models
from mptt.fields import TreeForeignKey

from marer import consts
from marer.models.base import *
from marer.models.base import finance_products_page_images_upload_path, news_pictures_upload_path, \
    showcase_partners_logos_upload_path
from marer.models.issue import *
from marer.models.issuer import *
from marer.models.user import *
from marer.products import get_finance_products_as_choices, get_finance_products


class FinanceProductPage(mptt_models.MPTTModel):

    class Meta:
        verbose_name = _('finance product')
        verbose_name_plural = _('finance products')

    name = models.CharField(verbose_name=_('finance product name'), max_length=512, blank=False, null=False)
    template = models.CharField(
        verbose_name='особый шаблон страницы',
        choices=[
            ('marer/product_custom_bg.html', 'Специальный шаблон для банковских гарантий'),
            ('marer/product_custom_credit.html', 'Специальный шаблон для кредитов'),
            ('marer/product_custom_factoring.html', 'Специальный шаблон для факторинга'),
            ('marer/product_custom_leasing.html', 'Специальный шаблон для лизинга'),
            ('marer/product_custom_gos_prog.html', 'Специальный шаблон для госпрограмм'),
        ],
        max_length=512,
        blank=True,
        null=True
    )
    parent = TreeForeignKey('self', verbose_name=_('parent product'), null=True, blank=True, related_name='childrens')
    _finance_product = models.CharField(
        verbose_name=_('linked finance product'),
        choices=get_finance_products_as_choices(),
        max_length=32,
        blank=True,
        null=True
    )
    _seo_h1 = models.CharField(verbose_name=_('name on page'), max_length=512, blank=True, null=False, default='')
    _seo_title = models.CharField(verbose_name=_('browser title'), max_length=512, blank=True, null=False, default='')
    _seo_description = models.CharField(
        verbose_name=_('page desctiption'),
        max_length=512,
        blank=True,
        null=False,
        default=''
    )
    _seo_keywords = models.CharField(
        verbose_name=_('page keywords'),
        max_length=512,
        blank=True,
        null=False,
        default=''
    )
    page_content = RichTextField(verbose_name=_('page content'), blank=True, null=False, default='')
    product_icon = models.ImageField(
        verbose_name=_('index page icon'),
        upload_to=finance_products_page_images_upload_path,
        blank=True,
        null=True
    )
    show_in_menu = BooleanField(verbose_name=_('show in menu'), default=True)

    def __str__(self):
        return self.name

    def get_seo_h1(self):
        return self._seo_h1 if self._seo_h1 != '' else self.name

    def get_seo_title(self):
        return self._seo_title if self._seo_title != '' else self.name

    def get_finance_product(self):
        if self._finance_product is not None:
            for fp in get_finance_products():
                if self._finance_product == fp.name:
                    return fp

        if self.parent is not None:
            return self.parent.get_finance_product()

        return None


class StaticPage(models.Model):

    class Meta:
        verbose_name = _('static page')
        verbose_name_plural = _('static pages')
        ordering = ['order']

    name = models.CharField(verbose_name=_('static page name'), max_length=512, blank=False, null=False)
    _seo_h1 = models.CharField(verbose_name=_('name on page'), max_length=512, blank=True, null=False, default='')
    _seo_title = models.CharField(verbose_name=_('browser title'), max_length=512, blank=True, null=False, default='')
    _seo_description = models.CharField(
        verbose_name=_('page desctiption'),
        max_length=512,
        blank=True,
        null=False,
        default=''
    )
    _seo_keywords = models.CharField(
        verbose_name=_('page keywords'),
        max_length=512,
        blank=True,
        null=False,
        default=''
    )
    page_content = RichTextField(verbose_name=_('page content'), blank=True, null=False, default='')
    order = models.PositiveIntegerField(blank=False, null=False, default=1)

    def __str__(self):
        return self.name

    def get_seo_h1(self):
        return self._seo_h1 if self._seo_h1 != '' else self.name

    def get_seo_title(self):
        return self._seo_title if self._seo_title != '' else self.name


class NewsPage(models.Model):

    class Meta:
        verbose_name = 'новость'
        verbose_name_plural = 'новости'
        ordering = ['-published_at']

    published_at = models.DateTimeField(verbose_name='дата и время публикации новости', blank=False, null=False)
    picture = models.ImageField(
        verbose_name='картинка к новости',
        upload_to=news_pictures_upload_path,
        blank=True,
        null=True
    )
    name = models.CharField(verbose_name='название новости', max_length=512, blank=False, null=False)
    _seo_h1 = models.CharField(verbose_name='название на странице', max_length=512, blank=True, null=False, default='')
    _seo_title = models.CharField(verbose_name='заголовок браузера', max_length=512, blank=True, null=False, default='')
    _seo_description = models.CharField(
        verbose_name='описание страницы',
        max_length=512,
        blank=True,
        null=False,
        default=''
    )
    _seo_keywords = models.CharField(
        verbose_name='ключевые слова страницы',
        max_length=512,
        blank=True,
        null=False,
        default=''
    )
    page_content = RichTextField(verbose_name='текст новости', blank=True, null=False, default='')

    def __str__(self):
        return self.name

    def get_seo_h1(self):
        return self._seo_h1 if self._seo_h1 != '' else self.name

    def get_seo_title(self):
        return self._seo_title if self._seo_title != '' else self.name


class ShowcasePartner(models.Model):

    class Meta:
        verbose_name = 'логотип партнера'
        verbose_name_plural = 'логотипы партнеров'

    logo = models.ImageField(
        verbose_name='логотип',
        upload_to=showcase_partners_logos_upload_path,
        blank=True,
        null=True
    )
    name = models.CharField(verbose_name='наименование', max_length=512, blank=False, null=False)
    category = models.CharField(verbose_name='категория', max_length=32, blank=False, null=False, choices=[
        (consts.SHOWCASE_PARTNERS_CATEGORY_BANKS, 'Банки'),
        (consts.SHOWCASE_PARTNERS_CATEGORY_INSURANCE, 'Страховые'),
        (consts.SHOWCASE_PARTNERS_CATEGORY_LEASING_FACTORING, 'Лизинговые и факторинговые'),
        (consts.SHOWCASE_PARTNERS_CATEGORY_GOS_PUB_FOUNDATIONS, 'Госструктуры, общественные организации и фонды'),
    ])

    def __str__(self):
        return self.name
