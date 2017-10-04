from django.db import models

from marer.models.base import OKVED2, Region
from marer.products import get_finance_products_as_choices


class FinanceOrganization(models.Model):
    name = models.CharField(max_length=512, blank=False, null=False)

    def __str__(self):
        return self.name


class FinanceOrgProductConditions(models.Model):
    INSURANCE_TYPE_REAL_ESTATE = 'real_estate'
    INSURANCE_TYPE_PLEDGE = 'pledge'

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
        (INSURANCE_TYPE_PLEDGE, 'Недвижимое имущество'),
        (INSURANCE_TYPE_PLEDGE, 'Залог'),
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
        if self.bg_insurance_type == FinanceOrgProductConditions.INSURANCE_TYPE_REAL_ESTATE:
            return 'Недвижимость'
        if self.bg_insurance_type == FinanceOrgProductConditions.INSURANCE_TYPE_PLEDGE:
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
