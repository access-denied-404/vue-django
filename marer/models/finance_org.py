from django.db import models


class FinanceOrganization(models.Model):
    name = models.CharField(max_length=512, blank=False, null=False)


class FinanceOrgProductConditions(models.Model):
    INSURANCE_TYPE_REAL_ESTATE = 'real_estate'
    INSURANCE_TYPE_PLEDGE = 'pledge'

    personal_presence_required = models.BooleanField(blank=True, null=False, default=False)

    bg_interest_rate = models.FloatField(blank=False, null=False, default=0)
    bg_review_term_days = models.PositiveIntegerField(blank=False, null=False, default=1)
    bg_insurance_type = models.CharField(choices=[
        (INSURANCE_TYPE_PLEDGE, 'Недвижимое имущество'),
        (INSURANCE_TYPE_PLEDGE, 'Залог'),
    ], blank=True, null=True)
    bg_insurance_value = models.PositiveSmallIntegerField(blank=False, null=False, default=0)
    bg_bank_account_opening_required = models.BooleanField(blank=True, null=False, default=False)
