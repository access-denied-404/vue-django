import base64
import datetime
import importlib
import os
import uuid
from logging import warning

from django.conf import settings
from django.db import models
from django.utils.encoding import force_str, force_text
from django.utils import timezone
from mptt import models as mptt_models
from mptt.fields import TreeForeignKey

from marer import consts

__all__ = ['Document', 'Region', 'RegionKLADRCode', 'BankMinimalCommission']


def documents_upload_path(instance, filename):
    new_filename = 'documents/%Y/%m/%d/{uuid}/{file_name}'.format(
        uuid=uuid.uuid4(),
        file_name=filename,
    )
    new_filename = force_str(new_filename)
    new_filename = datetime.datetime.now().strftime(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


def finance_products_page_images_upload_path(instance, filename):
    filename_arr = str(filename).split('.')
    ext = filename_arr[-1]
    new_filename = 'images/finance_products_page_images/{file_name}.{file_ext}'.format(
        file_name=uuid.uuid4(),
        file_ext=ext,
    )
    new_filename = force_str(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


def news_pictures_upload_path(instance, filename):
    filename_arr = str(filename).split('.')
    ext = filename_arr[-1]
    new_filename = 'images/news/{file_name}.{file_ext}'.format(
        file_name=uuid.uuid4(),
        file_ext=ext,
    )
    new_filename = force_str(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


def showcase_partners_logos_upload_path(instance, filename):
    filename_arr = str(filename).split('.')
    ext = filename_arr[-1]
    new_filename = 'images/showcase/partners/{file_name}.{file_ext}'.format(
        file_name=uuid.uuid4(),
        file_ext=ext,
    )
    new_filename = force_str(new_filename)
    new_filename = force_text(new_filename)
    new_filename = os.path.normpath(new_filename)
    return new_filename


def set_obj_update_time(obj, updated_at_field='updated_at'):
    if obj:
        if hasattr(obj, updated_at_field):
            setattr(obj, updated_at_field, timezone.now())
            obj.save()
        else:
            warning('Object {} got no field called {} for update time there'.format(
                obj, updated_at_field))
    else:
        warning('Got none object for set update time', stacklevel=3)


class Document(models.Model):

    file = models.FileField(upload_to=documents_upload_path, max_length=512)
    sign = models.FileField(upload_to=documents_upload_path, max_length=512, null=True, blank=True)

    sign_state = models.CharField(max_length=32, blank=True, null=False, default=consts.DOCUMENT_SIGN_NONE, choices=[
        (consts.DOCUMENT_SIGN_NONE, 'Отсутствует'),
        (consts.DOCUMENT_SIGN_CORRUPTED, 'Неверна'),
        (consts.DOCUMENT_SIGN_VERIFIED, 'Проверена'),
    ])

    def base64_content(self):
        if self.file and os.path.exists(self.file.path) and os.path.isfile(self.file.path):
            content = self.file.read()
            return base64.standard_b64encode(content)
        else:
            return ''

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        if not self.sign and self.sign_state != consts.DOCUMENT_SIGN_NONE:
            self.sign_state = consts.DOCUMENT_SIGN_NONE
            self.save()
        elif self.sign:
            sign_is_correct = False
            raw_check_sign_class = settings.FILE_SIGN_CHECK_CLASS
            if raw_check_sign_class is not None and raw_check_sign_class != '':
                raw_check_sign_class = str(raw_check_sign_class)
                check_sign_module_name, check_sign_class_name = raw_check_sign_class.rsplit('.', 1)
                check_sign_module = importlib.import_module(check_sign_module_name)
                check_sign_class = getattr(check_sign_module, check_sign_class_name)
                try:
                    sign_is_correct = check_sign_class.check_file_sign(self.file.path, self.sign.path)
                except Exception:
                    sign_is_correct = False
            if sign_is_correct and self.sign_state != consts.DOCUMENT_SIGN_VERIFIED:
                self.sign_state = consts.DOCUMENT_SIGN_VERIFIED
                self.save()
            elif not sign_is_correct and self.sign_state != consts.DOCUMENT_SIGN_CORRUPTED:
                self.sign_state = consts.DOCUMENT_SIGN_CORRUPTED
                self.save()


class OKVED2(mptt_models.MPTTModel):
    name = models.CharField(max_length=512, blank=False, null=False)
    code = models.CharField(max_length=32, blank=False, null=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='childrens')


class Region(mptt_models.MPTTModel):
    class Meta:
        verbose_name = 'регион'
        verbose_name_plural = 'регионы'

    name = models.CharField('название', max_length=512, blank=False, null=False)
    parent = TreeForeignKey('self', verbose_name='Родительский регион', null=True, blank=True, related_name='childrens')
    okato_code = models.CharField('код ОКАТО', max_length=32, blank=True, null=False, default='')
    oktmo_code = models.CharField('код ОКТМО', max_length=32, blank=True, null=False, default='')

    def __str__(self):
        return self.name


class RegionKLADRCode(models.Model):
    class Meta:
        verbose_name = 'код КЛАДР'
        verbose_name_plural = 'коды КЛАДР'

    region = TreeForeignKey(Region, verbose_name='регион', null=False, blank=False, related_name='kladr_codes')
    code = models.CharField('код КЛАДР', max_length=2, blank=True, null=False, default='')

    def __str__(self):
        return 'код КЛАДР региона «{}»: {}'.format(self.region, self.code)


class BankMinimalCommission(models.Model):
    class Meta:
        verbose_name = 'уровень минимальной комиссии банка'
        verbose_name_plural = 'уровни минимальной комиссии банка'

    sum_min = models.DecimalField(verbose_name='сумма продукта от', max_digits=12, decimal_places=2, blank=False, null=False)
    sum_max = models.DecimalField(verbose_name='сумма продукта по', max_digits=12, decimal_places=2, blank=False, null=False)
    commission = models.DecimalField(verbose_name='минимальная комиссия', max_digits=12, decimal_places=2, blank=False, null=False)
    term_months_min = models.IntegerField(verbose_name='срок действия продукта от, мес.', blank=False, null=False)
    term_months_max = models.IntegerField(verbose_name='срок действия продукта по, мес.', blank=False, null=False)

    def __str__(self):
        return '{} руб. при сумме с {} руб. по {} руб. c {} по {} мес.'.format(
            self.commission,
            self.sum_min,
            self.sum_max,
            self.term_months_min,
            self.term_months_max,
        )


class FormOwnership(models.Model):
    class Meta:
        verbose_name = 'форма собственности'
        verbose_name_plural = 'формы собственности'

    name = models.CharField(verbose_name='Форма собственности', max_length=100, blank=False, null=False)
    okopf_codes = models.CharField(max_length=256, verbose_name='Коды ОКОПФ', blank=False, null=False)

    def __str__(self):
        return self.name
