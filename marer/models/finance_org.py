from django.conf import settings
from django.db import models

from marer import consts
from marer.models.base import OKVED2, Region, Document
from marer.products import get_finance_products_as_choices, BankGuaranteeProduct


class FinanceOrganization(models.Model):
    class Meta:
        verbose_name = 'финансовая орнанизация'
        verbose_name_plural = 'финансовые организации'
        permissions = [
            # права менеджеров, управляющих финансовыми организациями
            ('can_change_managed_finance_orgs', 'Can change managed finance orgs'),
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

    class Meta:
        verbose_name = 'условия финансовой организации'
        verbose_name_plural = 'условия финансовых организаций'

    finance_product = models.CharField(
        max_length=32, choices=get_finance_products_as_choices(), null=False, blank=False)
    finance_org = models.ForeignKey(FinanceOrganization, verbose_name='Финансовая организация', null=False, blank=False, related_name='products_conditions')

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

    credit_tender_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_tender_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_tender_issue_rate = models.FloatField(verbose_name='Годовая ставка по тендерному кредиту', blank=True, null=True)
    credit_tender_interest_rate = models.FloatField(verbose_name='Годовая ставка по тендерному кредиту', blank=True, null=True)

    credit_contract_exec_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_contract_exec_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_contract_exec_issue_rate = models.FloatField(verbose_name='Годовая ставка по кредиту на исполнение контракта', blank=True, null=True)
    credit_contract_exec_interest_rate = models.FloatField(verbose_name='Годовая ставка по кредиту на исполнение контракта', blank=True, null=True)

    credit_work_capital_refill_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_work_capital_refill_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_work_capital_refill_issue_rate = models.FloatField(verbose_name='Годовая ставка по кредиту на пополнение оборотных средств', blank=True, null=True)
    credit_work_capital_refill_interest_rate = models.FloatField(verbose_name='Годовая ставка по кредиту на пополнение оборотных средств', blank=True, null=True)

    credit_overdraft_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_overdraft_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_overdraft_issue_rate = models.FloatField(verbose_name='Годовая ставка по овердрафту', blank=True, null=True)
    credit_overdraft_interest_rate = models.FloatField(verbose_name='Годовая ставка по овердрафту', blank=True, null=True)

    credit_renewable_credit_line_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_renewable_credit_line_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_renewable_credit_line_issue_rate = models.FloatField(verbose_name='Годовая ставка по ВКЛ', blank=True, null=True)
    credit_renewable_credit_line_interest_rate = models.FloatField(verbose_name='Годовая ставка по ВКЛ', blank=True, null=True)

    credit_project_financing_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_project_financing_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    credit_project_financing_issue_rate = models.FloatField(verbose_name='Годовая ставка по проектному финансированию', blank=True, null=True)
    credit_project_financing_interest_rate = models.FloatField(verbose_name='Годовая ставка по проектному финансированию', blank=True, null=True)

    leasing_min_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    leasing_max_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    leasing_interest_rate = models.FloatField(blank=True, null=True)

    def humanized_bg_insurance(self):
        if self.bg_insurance_type is None:
            return 'Нет'
        if self.bg_insurance_type == consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_REAL_ESTATE:
            return 'Недвижимость'
        if self.bg_insurance_type == consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_PLEDGE:
            return 'Залог {}%'.format(self.bg_insurance_value)
    humanized_bg_insurance.short_description = 'Требуемое обеспечение'
    humanized_bg_insurance.admin_order_field = 'bg_insurance_value'

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
    humanized_bg_review_tern_days.short_description = 'Время рассмотрения'
    humanized_bg_review_tern_days.admin_order_field = 'bg_review_term_days'

    def _humanized_bool_requirement_value(self, value):
        if value:
            return 'Нужно'
        else:
            return 'Не нужно'

    def humanized_bg_bank_account_opening_required(self):
        return self._humanized_bool_requirement_value(self.bg_bank_account_opening_required)
    humanized_bg_bank_account_opening_required.short_description = 'Открытие счета в банке'
    humanized_bg_bank_account_opening_required.admin_order_field = 'bg_bank_account_opening_required'

    def humanized_bg_personal_presence_required(self):
        return self._humanized_bool_requirement_value(self.personal_presence_required)
    humanized_bg_personal_presence_required.short_description = 'Личное присутствие'
    humanized_bg_personal_presence_required.admin_order_field = 'personal_presence_required'


class FinanceOrgProductProposeDocument(models.Model):
    class Meta:
        verbose_name = 'документ для банка'
        verbose_name_plural = 'документы для банка'

    finance_product = models.CharField(
        verbose_name='Финансовый продукт',
        max_length=32,
        choices=get_finance_products_as_choices(),
        null=False,
        blank=False
    )
    name = models.CharField(verbose_name='наименование', max_length=512, blank=False, null=False, default='')
    sample = models.ForeignKey(
        Document,
        verbose_name='образец',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fo_product_propose_samples_links'
    )
    code = models.CharField(
        verbose_name='вид общего документа',
        choices=[
            (consts.FO_PRODUCT_PROPOSE_DOC_HEAD_PASSPORT, 'Паспорт генерального директора (руководителя)'),
            (consts.FO_PRODUCT_PROPOSE_DOC_HEAD_STATUTE, 'Устав организации'),
        ],
        max_length=512,
        null=True,
        blank=True,
    )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.finance_product or self.finance_product == '':
            self.finance_product = BankGuaranteeProduct().name
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name or 'ДОКУМЕНТ БЕЗ НАЗВАНИЯ'
