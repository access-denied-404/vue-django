from django.forms import Form, CharField, ChoiceField, DateField, DecimalField, BooleanField, TextInput, DateInput, \
    IntegerField, HiddenInput, CheckboxInput, Select
from djangoformsetjs.utils import formset_media_js

from marer import consts


class BGFinProdRegForm(Form):
    issuer_full_name = CharField(required=False)
    issuer_short_name = CharField(required=False)
    issuer_legal_address = CharField(required=False)

    issuer_ogrn = CharField(required=False)
    issuer_inn = CharField(required=False)
    issuer_kpp = CharField(required=False)

    tender_gos_number = CharField(required=False)
    tender_placement_type = CharField(required=False)
    tender_exec_law = ChoiceField(required=False, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
        (consts.TENDER_EXEC_LAW_185_FZ, '185-ФЗ'),
        (consts.TENDER_EXEC_LAW_COMMERCIAL, 'Коммерческий'),
    ])
    tender_publish_date = DateField(required=False)
    tender_start_cost = DecimalField(decimal_places=2, required=False)

    tender_responsible_full_name = CharField(required=False)
    tender_responsible_legal_address = CharField(required=False)
    tender_responsible_inn = CharField(required=False)
    tender_responsible_kpp = CharField(required=False)
    tender_responsible_ogrn = CharField(required=False)

    bg_commercial_contract_subject = CharField(required=False)
    bg_commercial_contract_place_of_work = CharField(required=False)
    bg_commercial_contract_sum = DecimalField(decimal_places=2, required=False)
    bg_commercial_contract_sign_date = DateField(required=False)
    bg_commercial_contract_end_date = DateField(required=False)

    bg_sum = DecimalField(decimal_places=2, required=False)
    bg_currency = ChoiceField(required=False, choices=[
        (consts.CURRENCY_RUR, 'Рубль'),
        (consts.CURRENCY_USD, 'Доллар'),
        (consts.CURRENCY_EUR, 'Евро'),
    ])
    bg_start_date = DateField(required=False)
    bg_end_date = DateField(required=False)
    bg_deadline_date = DateField(required=False)
    bg_type = ChoiceField(required=False, choices=[
        (consts.BG_TYPE_APPLICATION_ENSURE, 'Обеспечение заявки'),
        (consts.BG_TYPE_CONTRACT_EXECUTION, 'Исполнение контракта'),
    ])

    tender_contract_type = ChoiceField(required=False, choices=[
        (consts.TENDER_CONTRACT_TYPE_SUPPLY_CONTRACT, 'Поставка товара'),
        (consts.TENDER_CONTRACT_TYPE_SERVICE_CONTRACT, 'Оказание услуг'),
        (consts.TENDER_CONTRACT_TYPE_WORKS_CONTRACT, 'Выполнение работ'),
    ])

    tender_has_prepayment = BooleanField(required=False)


class CreditFinProdRegForm(Form):
    credit_product_is_credit = BooleanField(required=False)
    credit_product_is_credit_line = BooleanField(required=False)
    credit_product_is_overdraft = BooleanField(required=False)

    credit_product_interest_rate = DecimalField(decimal_places=2, required=False)
    credit_repayment_schedule = ChoiceField(required=False, choices=[
        (consts.ISSUE_CREDIT_REPAYMENT_SCHEDULE_EQUAL_SHARES, 'Равными долями'),
        (consts.ISSUE_CREDIT_REPAYMENT_SCHEDULE_END_OF_TERM, 'В конце срока'),
    ])
    credit_product_term = CharField(required=False)
    credit_product_cl_tranche_term = CharField(required=False)
    credit_purpose_type = ChoiceField(required=False, choices=[
        (consts.CREDIT_PURPOSE_TYPE_WORK_CAPITAL_REFILL, 'Пополнение оборотных средств'),
        (consts.CREDIT_PURPOSE_TYPE_CONTRACT_EXEC, 'Исполнение контракта'),
    ])
    credit_purpose = CharField(required=False)
    credit_repayment_sources = CharField(required=False)

    bg_sum = DecimalField(decimal_places=2, required=False)
    bg_currency = ChoiceField(required=False, choices=[
        (consts.CURRENCY_RUR, 'Рубль'),
        (consts.CURRENCY_USD, 'Доллар'),
        (consts.CURRENCY_EUR, 'Евро'),
    ])

    issuer_full_name = CharField(required=False)
    issuer_short_name = CharField(required=False)
    issuer_legal_address = CharField(required=False)

    issuer_ogrn = CharField(required=False)
    issuer_inn = CharField(required=False)
    issuer_kpp = CharField(required=False)


class BGFinProdSurveyOrgCommonForm(Form):
    issuer_full_name = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_short_name = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_foreign_name = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_legal_address = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_fact_address = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_ogrn = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_inn = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_kpp = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_okpo = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_registration_date = DateField(required=False, widget=DateInput(attrs={'class': 'form-control'}))
    issuer_ifns_reg_date = DateField(required=False, widget=DateInput(attrs={'class': 'form-control'}))
    issuer_ifns_reg_cert_number = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_okopf = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_okved = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))


class BGFinProdSurveyOrgHeadForm(Form):
    issuer_head_first_name = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_last_name = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_middle_name = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_birthday = DateField(required=False, widget=DateInput(attrs={'class': 'form-control'}))
    issuer_head_org_position_and_permissions = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_phone = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_passport_series = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_passport_number = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_passport_issue_date = DateField(required=False, widget=DateInput(attrs={'class': 'form-control'}))
    issuer_head_passport_issued_by = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_residence_address = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_education_level = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_org_work_experience = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_share_in_authorized_capital = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_head_industry_work_experience = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))
    issuer_prev_org_info = CharField(required=False, widget=TextInput(attrs={'class': 'form-control'}))


class AffiliatesForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    name = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    legal_address = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    inn = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    activity_type = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    aff_percentage = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    aff_type = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    class Media(object):
        js = formset_media_js


class FounderLegalForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    name = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    add_date = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    additional_business = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    country = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    auth_capital_percentage = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    legal_address = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    class Media(object):
        js = formset_media_js


class FounderPhysicalForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    fio = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    add_date = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    additional_business = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    country = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    auth_capital_percentage = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    address = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    passport_data = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    class Media(object):
        js = formset_media_js


class CreditPledgeForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())

    pledge_title = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    pledge_type = ChoiceField(required=False, widget=Select(attrs={'class': 'form-control input-sm'}), choices=[
        (consts.CREDIT_PLEDGE_TYPE_DEPOSIT, 'Депозит'),
        (consts.CREDIT_PLEDGE_TYPE_REAL_ESTATE, 'Недвижимость'),
        (consts.CREDIT_PLEDGE_TYPE_OTHER, 'Другое'),
    ])
    cost = DecimalField(decimal_places=2, required=False, widget=TextInput(attrs={'class': 'form-control input-sm'}))

    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    def get_pledge_type_display(self):
        for val, val_name in self.fields['pledge_type'].choices:
            if val == self.initial.get('pledge_type', None):
                return val_name
        return ''

    class Media(object):
        js = formset_media_js


class LeasingFinProdRegForm(Form):
    leasing_term = IntegerField(required=False)
    leasing_advance_payment_rate = DecimalField(decimal_places=2, required=False)
    leasing_payment_schedule = CharField(required=False)
    leasing_asset_operation_territory = CharField(required=False)
    leasing_bank_account_number = CharField(required=False)
    leasing_corr_account_number = CharField(required=False)
    leasing_bank_name = CharField(required=False)
    leasing_bank_identification_code = CharField(required=False)
    leasing_holder_on_balance_name = CharField(required=False)
    leasing_holder_on_balance_ogrn = CharField(required=False)
    leasing_holder_on_balance_inn = CharField(required=False)
    leasing_holder_on_balance_kpp = CharField(required=False)
    leasing_insurer_name = CharField(required=False)
    leasing_insurer_ogrn = CharField(required=False)
    leasing_insurer_inn = CharField(required=False)
    leasing_insurer_kpp = CharField(required=False)


class LeasingAssetForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    supplier_name = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    asset_name = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    asset_spec = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    asset_count = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    cost_with_vat = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    supply_term = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    class Media(object):
        js = formset_media_js


class LeasingSupplierForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    supplier_name = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    supplier_head_fio = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    supplier_contact_fio = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    supplier_contacts = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    class Media(object):
        js = formset_media_js


class LeasingPayRuleForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    asset_name = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    payment_name = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    payment_size = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    payment_rule = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    class Media(object):
        js = formset_media_js


class FactoringFinProdRegForm(Form):
    factoring_product_is_regressive = BooleanField(required=False)
    factoring_product_is_not_regressive = BooleanField(required=False)
    factoring_product_is_cred_risks_cover = BooleanField(required=False)
    factoring_product_is_suppliers_financing = BooleanField(required=False)
    factoring_product_is_orders_financing = BooleanField(required=False)
    factoring_product_is_closed = BooleanField(required=False)
    factoring_product_is_export = BooleanField(required=False)
    factoring_product_is_import = BooleanField(required=False)
    factoring_avg_actual_buyers_payment_term = IntegerField(required=False)
    factoring_max_contract_deferred_payment_term = IntegerField(required=False)
    factoring_sale_goods_or_services = CharField(required=False)
    factoring_manufactured_goods = CharField(required=False)


class FactoringSalesAnalyzeForm(Form):
    curr_year_sales_value = DecimalField(decimal_places=2, required=False)
    prev_year_sales_value = DecimalField(decimal_places=2, required=False)
    curr_year_sales_value_inc_deferment = DecimalField(decimal_places=2, required=False)
    prev_year_sales_value_inc_deferment = DecimalField(decimal_places=2, required=False)
    curr_year_expected_sales_value = DecimalField(decimal_places=2, required=False)
    prev_year_expected_sales_value = DecimalField(decimal_places=2, required=False)
    curr_year_expected_sales_value_inc_deferment = DecimalField(decimal_places=2, required=False)
    prev_year_expected_sales_value_inc_deferment = DecimalField(decimal_places=2, required=False)


class FactoringBuyerForm(Form):
    id = IntegerField(required=False, widget=HiddenInput())
    name_and_inn = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    avg_monthly_shipments = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    operating_pay_deferment_days = IntegerField(required=False, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    start_work_date = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    required_credit_limit = DecimalField(decimal_places=2, required=False, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    debitor_share = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    average_delay_days = IntegerField(required=False, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    sales_volume = CharField(required=False, max_length=512, widget=TextInput(attrs={'class': 'form-control input-sm'}))
    DELETE = BooleanField(required=False, widget=CheckboxInput(attrs={'class': 'hidden'}))

    class Media(object):
        js = formset_media_js
