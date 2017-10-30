from django.conf import settings
from django.db import models

from marer import consts
from marer.models.base import OKVED2, Region, Document
from marer.products import get_finance_products_as_choices


class FinanceOrganization(models.Model):
    class Meta:
        verbose_name = 'финансовая орнанизация'
        verbose_name_plural = 'финансовые организации'
        permissions = [
            # права менеджеров, управляющих финансовыми организациями
            ('can_change_managed_finance_org_proposes', 'Can change managed finance org proposes'),
            ('can_view_managed_finance_org_proposes_issues', 'Can view managed finance org proposes issues'),
            ('can_add_managed_finance_org_proposes_clarifications', 'Can add managed finance org proposes clarifications'),
            ('can_view_managed_finance_org_proposes_clarifications', 'Can view managed finance org proposes clarifications'),
            ('can_add_managed_finance_org_proposes_clarifications_messages', 'Can add managed finance org proposes clarifications messages'),
        ]

    name = models.CharField(verbose_name='название', max_length=512, blank=False, null=False)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='менеджер',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class FinanceOrgProductConditions(models.Model):
    finance_product = models.CharField(
        max_length=32, choices=get_finance_products_as_choices(), null=False, blank=False)
    finance_org = models.ForeignKey(FinanceOrganization, null=False, blank=False, related_name='products_conditions')

    bg_44_app_ensure_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_44_app_ensure_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_44_app_ensure_interest_rate = models.FloatField(blank=True, null=True)

    bg_44_contract_exec_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_44_contract_exec_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_44_contract_exec_interest_rate = models.FloatField(blank=True, null=True)

    bg_223_app_ensure_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_223_app_ensure_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_223_app_ensure_interest_rate = models.FloatField(blank=True, null=True)

    bg_223_contract_exec_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_223_contract_exec_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_223_contract_exec_interest_rate = models.FloatField(blank=True, null=True)

    bg_185_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_185_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_185_interest_rate = models.FloatField(blank=True, null=True)

    bg_ct_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_ct_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_ct_interest_rate = models.FloatField(blank=True, null=True)

    bg_vat_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_vat_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_vat_interest_rate = models.FloatField(blank=True, null=True)

    bg_customs_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_customs_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    bg_customs_interest_rate = models.FloatField(blank=True, null=True)

    personal_presence_required = models.BooleanField(blank=True, null=False, default=False)
    bg_review_term_days = models.PositiveIntegerField(blank=False, null=False, default=1)
    bg_insurance_type = models.CharField(max_length=32, choices=[
        (consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_REAL_ESTATE, 'Недвижимое имущество'),
        (consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_PLEDGE, 'Залог'),
    ], blank=True, null=True)
    bg_insurance_value = models.PositiveSmallIntegerField(blank=False, null=False, default=0)
    bg_bank_account_opening_required = models.BooleanField(blank=True, null=False, default=False)
    bg_regions_blacklist = models.ManyToManyField(Region, blank=True)
    bg_sectors_blacklist = models.ManyToManyField(OKVED2, blank=True)

    credit_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_interest_rate = models.FloatField(blank=True, null=True)

    leasing_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    leasing_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    leasing_interest_rate = models.FloatField(blank=True, null=True)

    @property
    def humanized_bg_insurance(self):
        if self.bg_insurance_type is None:
            return 'Нет'
        if self.bg_insurance_type == consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_REAL_ESTATE:
            return 'Недвижимость'
        if self.bg_insurance_type == consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_PLEDGE:
            return 'Залог {}%'.format(self.bg_insurance_value)

    @property
    def humanized_bg_review_tern_days(self):

        days_cnt = self.bg_review_term_days
        days_cnt_str = str(days_cnt)
        last_digit = int(days_cnt_str[-1])
        if days_cnt > 9:
            last_two_digits = int(days_cnt_str[-2:])
        else:
            last_two_digits = 0

        if last_two_digits in [11, 12, 13, 14]:
            days_form = 'дней'
        elif last_digit in [1]:
            days_form = 'день'
        elif last_digit in [2, 3, 4]:
            days_form = 'дня'
        else:
            days_form = 'дней'
        return '{} {}'.format(days_cnt, days_form)

    def _humanized_bool_requirement_value(self, value):
        if value:
            return 'Нужно'
        else:
            return 'Не нужно'

    @property
    def humanized_bg_bank_account_opening_required(self):
        return self._humanized_bool_requirement_value(self.bg_bank_account_opening_required)

    @property
    def humanized_bg_personal_presence_required(self):
        return self._humanized_bool_requirement_value(self.personal_presence_required)


class FinanceOrgProductProposeDocument(models.Model):
    class Meta:
        verbose_name = 'документ для банка'
        verbose_name_plural = 'документы для банка'

    finance_product = models.CharField(
        max_length=32, choices=get_finance_products_as_choices(), null=False, blank=False)
    finance_org = models.ForeignKey(FinanceOrganization, null=False, blank=False, related_name='products_docs_samples')
    name = models.CharField(max_length=512, blank=False, null=False, default='')
    sample = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fo_product_propose_samples_links'
    )
    code = models.CharField(
        choices=[
            (consts.FO_PRODUCT_PROPOSE_DOC_HEAD_PASSPORT, 'Паспорт генерального директора (руководителя)'),
            (consts.FO_PRODUCT_PROPOSE_DOC_HEAD_STATUTE, 'Устав организации'),
        ],
        max_length=512,
        null=True,
        blank=True,
    )
