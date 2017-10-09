from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.forms import formset_factory

from django.forms.forms import Form
from django.forms.fields import CharField, DecimalField, DateField, ChoiceField, BooleanField, IntegerField
from django.forms.widgets import TextInput, DateInput, HiddenInput, CheckboxInput
from django.utils import timezone
from djangoformsetjs.utils import formset_media_js

from marer import consts
from marer.products.base import FinanceProduct, FinanceProductDocumentItem


def _get_subclasses_recursive(cls: type) -> list:
    """
    Поиск всех классов, наследующий указанный класс.
    Подклассы подклассов также рекурсивно учитывается
    """
    subclasses = cls.__subclasses__()
    more_subclasses = []
    for sub_cls in subclasses:
        more_subclasses.extend(_get_subclasses_recursive(sub_cls))
    subclasses.extend(more_subclasses)
    return subclasses


def get_finance_products():
    products_subclasses = _get_subclasses_recursive(FinanceProduct)
    return [ps() for ps in products_subclasses]


def get_finance_products_as_choices():
    products_objs = get_finance_products()
    return [(po.name, po.humanized_name) for po in products_objs]


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


class BankGuaranteeProduct(FinanceProduct):
    _humanized_name = 'Банковская гарантия'
    _survey_template_name = 'marer/products/BankGuarantee/form_survey.html'

    def get_documents_list(self, now_override=None):
        docs = []

        # here we getting a list with ends of year quarters
        if now_override is None:
            curr_localized_datetime = timezone.localtime(timezone.now(), timezone.get_current_timezone())
        else:
            curr_localized_datetime = timezone.localtime(now_override, timezone.get_current_timezone())

        curr_date = curr_localized_datetime.date()

        prev_month_start_date = (curr_date - relativedelta(months=1)).replace(day=1)
        yr_quartals_start_months = [1, 4, 7, 10]
        curr_quartal_start_date = prev_month_start_date
        while curr_quartal_start_date.month not in yr_quartals_start_months:
            curr_quartal_start_date -= relativedelta(months=1)
        yr_quarters_cnt = 4  # first quarter will catch as finished quarter on start
        quarters_start_date = curr_quartal_start_date - relativedelta(months=yr_quarters_cnt*3)
        quarters_curr_date = quarters_start_date

        while quarters_curr_date <= prev_month_start_date:

            fpdi_code, fpdi_name = self._build_accounting_report_common_doc_code_and_name_by_next_quarter_start_date(quarters_curr_date)

            docs.append(FinanceProductDocumentItem(code=fpdi_code, name=fpdi_name, description='Формы 1 и 2'))
            quarters_curr_date += relativedelta(months=3)

        docs.extend([
            FinanceProductDocumentItem(
                code='loans_description_yr{}_m{}'.format(curr_date.year, curr_date.month),
                name='Расшифровка кредитов и займов',
                description='По состоянию на текущую дату',
            ),
            FinanceProductDocumentItem(
                code='contracts_registry_yr{}_m{}'.format(curr_date.year, curr_date.month),
                name='Реестр контрактов',
            ),
        ])
        return docs

    def _build_accounting_report_common_doc_code_and_name_by_next_quarter_start_date(self, next_quarter_start_date):
        quarter_number = int((next_quarter_start_date - relativedelta(days=1)).month / 3)

        if quarter_number == 4:
            fpdi_code = 'accounting_report_forms_1_2_for_y{}'.format(
                (next_quarter_start_date - relativedelta(days=1)).strftime('%Y')
            )
        else:
            fpdi_code = 'accounting_report_forms_1_2_for_y{}q{}'.format(
                (next_quarter_start_date - relativedelta(days=1)).strftime('%Y'),
                quarter_number,
            )

        if quarter_number in [1, 3]:
            fpdi_name = 'Бухгалтерская отчетность за {} квартал {} года'.format(
                quarter_number,
                next_quarter_start_date.strftime('%Y'))
        elif quarter_number == 2:
            fpdi_name = 'Бухгалтерская отчетность за первое полугодие {} года'.format(
                next_quarter_start_date.strftime('%Y'))
        elif quarter_number == 4:
            fpdi_name = 'Бухгалтерская отчетность за {} год'.format(
                (next_quarter_start_date - relativedelta(days=1)).strftime('%Y'))

        return fpdi_code, fpdi_name

    def get_registering_form_class(self):
        return BGFinProdRegForm

    def get_survey_context_part(self):
        affiliates_formset = formset_factory(AffiliatesForm, extra=0)
        from marer.models.issue import IssueBGProdAffiliate
        affiliates = IssueBGProdAffiliate.objects.filter(issue=self._issue)
        affiliates_formset = affiliates_formset(initial=[aff.__dict__ for aff in affiliates], prefix='aff')

        formset_founders_legal = formset_factory(FounderLegalForm, extra=0)
        from marer.models.issue import IssueBGProdFounderLegal
        founders_legal = IssueBGProdFounderLegal.objects.filter(issue=self._issue)
        formset_founders_legal = formset_founders_legal(initial=[fl.__dict__ for fl in founders_legal], prefix='founders_legal')

        formset_founders_physical = formset_factory(FounderPhysicalForm, extra=0)
        from marer.models.issue import IssueBGProdFounderPhysical
        founders_physical = IssueBGProdFounderPhysical.objects.filter(issue=self._issue)
        formset_founders_physical = formset_founders_physical(initial=[fp.__dict__ for fp in founders_physical], prefix='founders_physical')

        return dict(
            form_org_common=BGFinProdSurveyOrgCommonForm(initial=self._issue.__dict__),
            form_org_head=BGFinProdSurveyOrgHeadForm(initial=self._issue.__dict__),
            affiliates_formset=affiliates_formset,
            formset_founders_legal=formset_founders_legal,
            formset_founders_physical=formset_founders_physical,
        )

    def process_survey_post_data(self, request):
        form_org_common = BGFinProdSurveyOrgCommonForm(request.POST)
        if form_org_common.is_valid():
            self._issue.issuer_full_name = form_org_common.cleaned_data['issuer_full_name']
            self._issue.issuer_short_name = form_org_common.cleaned_data['issuer_short_name']

            self._issue.issuer_ogrn = form_org_common.cleaned_data['issuer_ogrn']
            self._issue.issuer_inn = form_org_common.cleaned_data['issuer_inn']
            self._issue.issuer_kpp = form_org_common.cleaned_data['issuer_kpp']

            self._issue.issuer_foreign_name = form_org_common.cleaned_data['issuer_foreign_name']
            self._issue.issuer_legal_address = form_org_common.cleaned_data['issuer_legal_address']
            self._issue.issuer_fact_address = form_org_common.cleaned_data['issuer_fact_address']
            self._issue.issuer_okpo = form_org_common.cleaned_data['issuer_okpo']
            self._issue.issuer_registration_date = form_org_common.cleaned_data['issuer_registration_date']
            self._issue.issuer_ifns_reg_date = form_org_common.cleaned_data['issuer_ifns_reg_date']
            self._issue.issuer_ifns_reg_cert_number = form_org_common.cleaned_data['issuer_ifns_reg_cert_number']
            self._issue.issuer_okopf = form_org_common.cleaned_data['issuer_okopf']
            self._issue.issuer_okved = form_org_common.cleaned_data['issuer_okved']

        form_org_head = BGFinProdSurveyOrgHeadForm(request.POST)
        if form_org_head.is_valid():
            self._issue.issuer_head_first_name = form_org_head.cleaned_data['issuer_head_first_name']
            self._issue.issuer_head_last_name = form_org_head.cleaned_data['issuer_head_last_name']
            self._issue.issuer_head_middle_name = form_org_head.cleaned_data['issuer_head_middle_name']
            self._issue.issuer_head_birthday = form_org_head.cleaned_data['issuer_head_birthday']

            self._issue.issuer_head_org_position_and_permissions = form_org_head.cleaned_data['issuer_head_org_position_and_permissions']
            self._issue.issuer_head_phone = form_org_head.cleaned_data['issuer_head_phone']

            self._issue.issuer_head_passport_series = form_org_head.cleaned_data['issuer_head_passport_series']
            self._issue.issuer_head_passport_number = form_org_head.cleaned_data['issuer_head_passport_number']
            self._issue.issuer_head_passport_issue_date = form_org_head.cleaned_data['issuer_head_passport_issue_date']
            self._issue.issuer_head_passport_issued_by = form_org_head.cleaned_data['issuer_head_passport_issued_by']
            self._issue.issuer_head_residence_address = form_org_head.cleaned_data['issuer_head_residence_address']

            self._issue.issuer_head_education_level = form_org_head.cleaned_data['issuer_head_education_level']
            self._issue.issuer_head_org_work_experience = form_org_head.cleaned_data['issuer_head_org_work_experience']
            self._issue.issuer_head_share_in_authorized_capital = form_org_head.cleaned_data['issuer_head_share_in_authorized_capital']
            self._issue.issuer_head_industry_work_experience = form_org_head.cleaned_data['issuer_head_industry_work_experience']
            self._issue.issuer_prev_org_info = form_org_head.cleaned_data['issuer_prev_org_info']

        self._issue.save()

        # processing legal founders
        formset_founders_legal = formset_factory(FounderLegalForm, extra=0)
        formset_founders_legal = formset_founders_legal(request.POST, prefix='founders_legal')
        from marer.models.issue import IssueBGProdFounderLegal
        if formset_founders_legal.is_valid():
            for afdata in formset_founders_legal.cleaned_data:
                afdata_id = afdata.get('id', None)
                afdata_name = str(afdata.get('name', '')).strip()
                if afdata_id and afdata.get('DELETE', False):
                    try:
                        lf = IssueBGProdFounderLegal.objects.get(id=afdata['id'], issue=self._issue)
                        lf.delete()
                    except ObjectDoesNotExist:
                        pass  # nothing to do

                elif not afdata_id and afdata_name != '':
                    new_lf = IssueBGProdFounderLegal()
                    new_lf.name = afdata_name
                    new_lf.add_date = afdata.get('add_date', '')
                    new_lf.additional_business = afdata.get('additional_business', '')
                    new_lf.country = afdata.get('country', '')
                    new_lf.auth_capital_percentage = afdata.get('auth_capital_percentage', '')
                    new_lf.legal_address = afdata.get('legal_address', '')
                    new_lf.issue = self._issue
                    new_lf.save()

        # processing physical founders
        formset_founders_physical = formset_factory(FounderPhysicalForm, extra=0)
        formset_founders_physical = formset_founders_physical(request.POST, prefix='founders_physical')
        from marer.models.issue import IssueBGProdFounderPhysical
        if formset_founders_physical.is_valid():
            for afdata in formset_founders_physical.cleaned_data:
                afdata_id = afdata.get('id', None)
                afdata_fio = str(afdata.get('fio', '')).strip()
                if afdata_id and afdata.get('DELETE', False):
                    try:
                        pf = IssueBGProdFounderPhysical.objects.get(id=afdata['id'], issue=self._issue)
                        pf.delete()
                    except ObjectDoesNotExist:
                        pass  # nothing to do

                elif not afdata_id and afdata_fio != '':
                    new_pf = IssueBGProdFounderPhysical()
                    new_pf.fio = afdata_fio
                    new_pf.add_date = afdata.get('add_date', '')
                    new_pf.additional_business = afdata.get('additional_business', '')
                    new_pf.country = afdata.get('country', '')
                    new_pf.auth_capital_percentage = afdata.get('auth_capital_percentage', '')
                    new_pf.address = afdata.get('address', '')
                    new_pf.passport_data = afdata.get('passport_data', '')
                    new_pf.issue = self._issue
                    new_pf.save()

        # processing affiliates
        from marer.models.issue import IssueBGProdAffiliate
        affiliates_formset = formset_factory(AffiliatesForm, extra=0)
        aff_formset = affiliates_formset(request.POST, prefix='aff')
        if aff_formset.is_valid():
            for afdata in aff_formset.cleaned_data:
                afdata_id = afdata.get('id', None)
                afdata_name = str(afdata.get('name', '')).strip()
                if afdata_id and afdata.get('DELETE', False):
                    try:
                        aff = IssueBGProdAffiliate.objects.get(id=afdata['id'], issue=self._issue)
                        aff.delete()
                    except ObjectDoesNotExist:
                        pass  # nothing to do

                elif not afdata_id and afdata_name != '':
                    new_aff = IssueBGProdAffiliate()
                    new_aff.name = afdata_name
                    new_aff.legal_address = afdata.get('legal_address', '')
                    new_aff.inn = afdata.get('inn', '')
                    new_aff.activity_type = afdata.get('activity_type', '')
                    new_aff.aff_percentage = afdata.get('aff_percentage', '')
                    new_aff.aff_type = afdata.get('aff_type', '')
                    new_aff.issue = self._issue
                    new_aff.save()

    def process_registering_form(self, request):
        self._issue.refresh_from_db()
        form_class = self.get_registering_form_class()
        form = form_class(request.POST)
        form.full_clean()
        for field in form.cleaned_data:
            setattr(self._issue, field, form.cleaned_data[field])
        self._issue.save()

    def get_admin_issue_fieldset(self):
        return [
            ('Issuer info', dict(fields=(
                'bg_sum',
                'bg_currency',
                'bg_start_date',
                'bg_end_date',
                'bg_deadline_date',
                'bg_type',
            ))),

            ('Tender info', dict(fields=(
                'tender_gos_number',
                'tender_placement_type',
                'tender_exec_law',
                'tender_publish_date',
                'tender_start_cost',
                'tender_contract_type',
                'tender_has_prepayment',
            ))),

            ('Issuer info', dict(classes=('collapse',), fields=(
                'issuer_full_name',
                'issuer_short_name',
                'issuer_foreign_name',
                'issuer_ogrn',
                'issuer_inn',
                'issuer_kpp',
                'issuer_legal_address',
                'issuer_fact_address',

                'issuer_okpo',
                'issuer_registration_date',
                'issuer_ifns_reg_date',
                'issuer_ifns_reg_cert_number',
                'issuer_okopf',
                'issuer_okved',
            ))),

            ('Issuer head', dict(classes=('collapse',), fields=(
                'issuer_head_first_name',
                'issuer_head_last_name',
                'issuer_head_middle_name',
                'issuer_head_birthday',
                'issuer_head_org_position_and_permissions',

                'issuer_head_phone',
                'issuer_head_passport_series',
                'issuer_head_passport_number',
                'issuer_head_passport_issue_date',
                'issuer_head_passport_issued_by',
                'issuer_head_residence_address',

                'issuer_head_education_level',
                'issuer_head_org_work_experience',
                'issuer_head_share_in_authorized_capital',
                'issuer_head_industry_work_experience',
                'issuer_prev_org_info',
            ))),

            ('Tender responsible info', dict(classes=('collapse',), fields=(
                'tender_responsible_full_name',
                'tender_responsible_legal_address',
                'tender_responsible_ogrn',
                'tender_responsible_inn',
                'tender_responsible_kpp',
            ))),
        ]


class CreditProduct(FinanceProduct):
    _humanized_name = 'Кредит'

    def get_documents_list(self):
        return []

    def get_registering_form_class(self):
        return Form


class LeasingProduct(FinanceProduct):
    _humanized_name = 'Лизинг'

    def get_documents_list(self):
        return []

    def get_registering_form_class(self):
        return Form
