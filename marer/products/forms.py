from django.forms import Form, CharField, ChoiceField, DateField, DecimalField, BooleanField, TextInput, DateInput, \
    IntegerField, HiddenInput, CheckboxInput
from djangoformsetjs.utils import formset_media_js

from marer import consts


class BGFinProdRegForm(Form):
    issuer_full_name = CharField(required=False)
    issuer_short_name = CharField(required=False)
    issuer_legal_address = CharField(required=False)

    issuer_ogrn = CharField(required=False)
    issuer_inn = CharField(required=False)
    issuer_kpp = CharField(required=False)

    tender_gos_number = CharField(required=True)
    tender_placement_type = CharField(required=False)
    tender_exec_law = ChoiceField(required=False, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
    ])
    tender_publish_date = DateField(required=False)
    tender_start_cost = DecimalField(decimal_places=2, required=False)

    tender_responsible_full_name = CharField(required=False)
    tender_responsible_legal_address = CharField(required=False)
    tender_responsible_inn = CharField(required=False)
    tender_responsible_kpp = CharField(required=False)
    tender_responsible_ogrn = CharField(required=False)

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