from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.formats import number_format
from django.utils.translation import ugettext_lazy as _
from mptt import models as mptt_models
from mptt.fields import TreeForeignKey


class Issuer(models.Model):
    inn = models.CharField(max_length=32, blank=False, null=False)
    kpp = models.CharField(max_length=32, blank=False, null=False)
    ogrn = models.CharField(max_length=32, blank=False, null=False)
    full_name = models.CharField(max_length=512, blank=False, null=False)
    short_name = models.CharField(max_length=512, blank=False, null=False)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)


class User(AbstractUser):
    phone = models.CharField(_('contact phone'), max_length=30, blank=True)

    @classmethod
    def normalize_username(cls, username):
        username = super().normalize_username(username)
        return str(username).lower()


class FinanceOrganization(models.Model):
    name = models.CharField(max_length=512, blank=False, null=False)
    interest_rate = models.FloatField(blank=False, null=False, default=0)
    review_term_days = models.PositiveIntegerField(blank=False, null=False, default=1)


class OKVED2(mptt_models.MPTTModel):
    name = models.CharField(max_length=512, blank=False, null=False)
    code = models.CharField(max_length=32, blank=False, null=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='childrens')


class Region(mptt_models.MPTTModel):
    name = models.CharField(max_length=512, blank=False, null=False)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='childrens')


class FinanceProduct(mptt_models.MPTTModel):

    class Meta:
        verbose_name = _('finance product')
        verbose_name_plural = _('finance products')

    name = models.CharField(verbose_name=_('finance product name'), max_length=512, blank=False, null=False)
    parent = TreeForeignKey('self', verbose_name=_('parent product'), null=True, blank=True, related_name='childrens')
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

    def __str__(self):
        return self.name

    def get_seo_h1(self):
        return self._seo_h1 if self._seo_h1 != '' else self.name

    def get_seo_title(self):
        return self._seo_title if self._seo_title != '' else self.name


class IssueDocument(models.Model):
    pass


class IssueDocumentRequest(models.Model):
    pass


class Issue(models.Model):
    STATUS_REGISTERING = 'registering'
    STATUS_COMMON_DOCUMENTS_REQUEST = 'common_documents_request'
    STATUS_SURVEY = 'survey'
    STATUS_SCORING = 'scoring'
    STATUS_ADDITIONAL_DOCUMENTS_REQUEST = 'additional_documents_request'
    STATUS_PAYMENTS = 'payments'
    STATUS_FINAL_DOCUMENTS_APPROVAL = 'final_documents_approval'
    STATUS_FINISHED = 'finished'
    STATUS_CANCELLED = 'cancelled'

    type = models.ForeignKey(FinanceProduct, on_delete=models.DO_NOTHING, null=False)
    status = models.CharField(max_length=32, blank=False, null=False, choices=[
        (STATUS_REGISTERING, 'Оформление заявки'),
        (STATUS_COMMON_DOCUMENTS_REQUEST, 'Запрос документов'),
        (STATUS_SURVEY, 'Анкетирование'),
        (STATUS_SCORING, 'Скоринг'),
        (STATUS_ADDITIONAL_DOCUMENTS_REQUEST, 'Дозапрос документов'),
        (STATUS_PAYMENTS, 'Оплата услуг'),
        (STATUS_FINAL_DOCUMENTS_APPROVAL, 'Согласование итоговых документов'),
        (STATUS_FINISHED, 'Завершена'),
        (STATUS_CANCELLED, 'Отменена'),
    ])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False)
    sum = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    issuer = models.CharField(max_length=512, blank=True, null=False, default='')

    @property
    def humanized_id(self):
        if self.id:
            return str(self.id).zfill(10)
        else:
            return 'БЕЗ НОМЕРА'

    @property
    def humanized_sum(self):
        if self.sum:
            fmt_sum = number_format(self.sum)
            currency = 'руб.'
            return fmt_sum + ' ' + currency
        else:
            return '—'

    @property
    def humanized_status(self):
        return self.get_status_display()
