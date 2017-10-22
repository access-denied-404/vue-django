import logging
import warnings

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.forms import formset_factory
from django.forms.forms import Form
from django.utils import timezone

from marer import consts
from marer.products.base import FinanceProduct, FinanceProductDocumentItem
from marer.products.forms import BGFinProdRegForm, BGFinProdSurveyOrgCommonForm, BGFinProdSurveyOrgHeadForm, \
    AffiliatesForm, FounderLegalForm, FounderPhysicalForm, CreditFinProdRegForm, CreditPledgeForm
from marer.utils.loadfoc import get_cell_value, get_cell_summ_range, get_cell_percentage, get_cell_bool, \
    get_cell_review_term_days, get_cell_ensure_condition


logger = logging.getLogger('django')

_admin_issue_fieldset_issuer_part = (
    'Сведения о компании-заявителе',
    dict(
        classes=('collapse',),
        fields=(
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
        )
    )
)

_admin_issue_fieldset_issuer_head_part = (
    'Руководитель компании',
    dict(
        classes=('collapse',),
        fields=(
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
        )
    )
)


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


def _build_accounting_report_common_doc_code_and_name_by_next_quarter_start_date(next_quarter_start_date):
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
    else:
        raise ValueError('Could not determine issue common document name for accounting report basing on year quarter')

    return fpdi_code, fpdi_name


def get_finance_products():
    products_subclasses = _get_subclasses_recursive(FinanceProduct)
    return [ps() for ps in products_subclasses]


def get_finance_products_as_choices():
    products_objs = get_finance_products()
    return [(po.name, po.humanized_name) for po in products_objs]


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

            fpdi_code, fpdi_name = _build_accounting_report_common_doc_code_and_name_by_next_quarter_start_date(
                quarters_curr_date)

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
        formset_founders_legal = formset_founders_legal(
            initial=[fl.__dict__ for fl in founders_legal],
            prefix='founders_legal'
        )

        formset_founders_physical = formset_factory(FounderPhysicalForm, extra=0)
        from marer.models.issue import IssueBGProdFounderPhysical
        founders_physical = IssueBGProdFounderPhysical.objects.filter(issue=self._issue)
        formset_founders_physical = formset_founders_physical(
            initial=[fp.__dict__ for fp in founders_physical],
            prefix='founders_physical'
        )

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

            self._issue.issuer_head_org_position_and_permissions = form_org_head.cleaned_data[
                'issuer_head_org_position_and_permissions']
            self._issue.issuer_head_phone = form_org_head.cleaned_data['issuer_head_phone']

            self._issue.issuer_head_passport_series = form_org_head.cleaned_data['issuer_head_passport_series']
            self._issue.issuer_head_passport_number = form_org_head.cleaned_data['issuer_head_passport_number']
            self._issue.issuer_head_passport_issue_date = form_org_head.cleaned_data['issuer_head_passport_issue_date']
            self._issue.issuer_head_passport_issued_by = form_org_head.cleaned_data['issuer_head_passport_issued_by']
            self._issue.issuer_head_residence_address = form_org_head.cleaned_data['issuer_head_residence_address']

            self._issue.issuer_head_education_level = form_org_head.cleaned_data['issuer_head_education_level']
            self._issue.issuer_head_org_work_experience = form_org_head.cleaned_data['issuer_head_org_work_experience']
            self._issue.issuer_head_share_in_authorized_capital = form_org_head.cleaned_data[
                'issuer_head_share_in_authorized_capital']
            self._issue.issuer_head_industry_work_experience = form_org_head.cleaned_data[
                'issuer_head_industry_work_experience']
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

    def get_admin_issue_fieldset(self):
        return [
            ('Сведения об истребуемой гарантии', dict(fields=(
                ('bg_sum', 'bg_currency',),
                ('bg_start_date', 'bg_end_date',),
                'bg_deadline_date',
                'bg_type',
            ))),

            ('Сведения о тендере', dict(classes=('collapse',), fields=(
                'tender_gos_number',
                'tender_placement_type',
                'tender_exec_law',
                'tender_publish_date',
                'tender_start_cost',
                'tender_contract_type',
                'tender_has_prepayment',
            ))),

            _admin_issue_fieldset_issuer_part,
            _admin_issue_fieldset_issuer_head_part,

            ('Сведения об организаторе тендера', dict(classes=('collapse',), fields=(
                'tender_responsible_full_name',
                'tender_responsible_legal_address',
                'tender_responsible_ogrn',
                'tender_responsible_inn',
                'tender_responsible_kpp',
            ))),
        ]

    def get_finance_orgs_conditions_list_fields(self):

        # any field just to fall avoid
        interest_rate_field_name = 'bg_44_app_ensure_interest_rate'

        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_44_FZ:
            if self._issue.bg_type == consts.BG_TYPE_APPLICATION_ENSURE:
                interest_rate_field_name = 'bg_44_app_ensure_interest_rate'
            elif self._issue.bg_type == consts.BG_TYPE_CONTRACT_EXECUTION:
                interest_rate_field_name = 'bg_44_contract_exec_interest_rate'
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_223_FZ:
            if self._issue.bg_type == consts.BG_TYPE_APPLICATION_ENSURE:
                interest_rate_field_name = 'bg_223_app_ensure_interest_rate'
            elif self._issue.bg_type == consts.BG_TYPE_CONTRACT_EXECUTION:
                interest_rate_field_name = 'bg_223_contract_exec_interest_rate'

        return [
            (interest_rate_field_name, 'Процентная ставка'),
            ('humanized_bg_insurance', 'Обеспечение'),
            ('humanized_bg_review_tern_days', 'Срок рассмотрения'),
            ('humanized_bg_bank_account_opening_required', 'Открытие р/с'),
            ('humanized_bg_personal_presence_required', 'Личное присутствие'),
        ]

    def get_finance_orgs_conditions_list(self):
        from marer.models.finance_org import FinanceOrgProductConditions
        qs = FinanceOrgProductConditions.objects.filter(
            finance_product=self.name,
            bg_review_term_days__gt=0,
        )

        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_44_FZ:
            if self._issue.bg_type == consts.BG_TYPE_APPLICATION_ENSURE:
                qs = qs.filter(bg_44_app_ensure_interest_rate__isnull=False)
            elif self._issue.bg_type == consts.BG_TYPE_CONTRACT_EXECUTION:
                qs = qs.filter(bg_44_contract_exec_interest_rate__isnull=False)
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_223_FZ:
            if self._issue.bg_type == consts.BG_TYPE_APPLICATION_ENSURE:
                qs = qs.filter(bg_223_app_ensure_interest_rate__isnull=False)
            elif self._issue.bg_type == consts.BG_TYPE_CONTRACT_EXECUTION:
                qs = qs.filter(bg_223_contract_exec_interest_rate__isnull=False)

        return qs

    def load_finance_orgs_conditions_from_worksheet(self, ws):
        """
        HEADERS

            A1:A3   Bank name
            B1:E1   44-FZ section
            B2:C2       application ensure
            B3              sum
            C3              percent
            D2:E2       contract execute ensure
            D3              sum
            E3              percent
            F1:I1   223-FZ
            F2:G2       application ensure
            F3              sum
            G3              percent
            H2:I2       contract execute ensure
            H3              sum
            I3              percent
            J1:K1   185-FZ
            J2:J3       sum
            K2:K3       percent
            L1:M1   Commercical
            L2:L3       sum
            M2:M3       percent
            N1:O1   VAT
            N2:N3       sum
            O2:O3       percent
            P1:Q1   Customs
            P2:P3       sum
            Q2:Q3       percent
            R1:R3   Personal presence requirement
            S1:S3   Review term days
            T1:T3   Insurance
            U1:U3   Bank account opening requirement
            V1:W1   Regions
            V2:V3       blacklist
            W2:W3       whitelist
        """
        idx = 4

        bank_name = get_cell_value(ws, 'a', idx).value
        while bank_name is not None and bank_name != '':

            from marer.models.finance_org import FinanceOrgProductConditions
            new_foc = FinanceOrgProductConditions()

            try:
                # Subtypes conditions
                # 44-FZ
                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'b', idx))
                new_foc.bg_44_app_ensure_min_sum = min_sum
                new_foc.bg_44_app_ensure_max_sum = max_sum
                new_foc.bg_44_app_ensure_interest_rate = get_cell_percentage(get_cell_value(ws, 'c', idx))

                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'd', idx))
                new_foc.bg_44_contract_exec_min_sum = min_sum
                new_foc.bg_44_contract_exec_max_sum = max_sum
                new_foc.bg_44_contract_exec_interest_rate = get_cell_percentage(get_cell_value(ws, 'e', idx))

                # 223-FZ
                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'f', idx))
                new_foc.bg_223_app_ensure_min_sum = min_sum
                new_foc.bg_223_app_ensure_max_sum = max_sum
                new_foc.bg_223_app_ensure_interest_rate = get_cell_percentage(get_cell_value(ws, 'g', idx))

                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'h', idx))
                new_foc.bg_223_contract_exec_min_sum = min_sum
                new_foc.bg_223_contract_exec_max_sum = max_sum
                new_foc.bg_223_contract_exec_interest_rate = get_cell_percentage(get_cell_value(ws, 'i', idx))

                # 185-FZ
                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'j', idx))
                new_foc.bg_185_min_sum = min_sum
                new_foc.bg_185_max_sum = max_sum
                new_foc.bg_185_interest_rate = get_cell_percentage(get_cell_value(ws, 'k', idx))

                # Commercial
                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'l', idx))
                new_foc.bg_ct_min_sum = min_sum
                new_foc.bg_ct_max_sum = max_sum
                new_foc.bg_ct_interest_rate = get_cell_percentage(get_cell_value(ws, 'm', idx))

                # VAT
                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'n', idx))
                new_foc.bg_vat_min_sum = min_sum
                new_foc.bg_vat_max_sum = max_sum
                new_foc.bg_vat_interest_rate = get_cell_percentage(get_cell_value(ws, 'o', idx))

                # Customs
                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'p', idx))
                new_foc.bg_customs_min_sum = min_sum
                new_foc.bg_customs_max_sum = max_sum
                new_foc.bg_customs_interest_rate = get_cell_percentage(get_cell_value(ws, 'q', idx))

                # Base conditions
                new_foc.personal_presence_required = get_cell_bool(get_cell_value(ws, 'r', idx))
                new_foc.bg_review_term_days = get_cell_review_term_days(get_cell_value(ws, 's', idx))

                ensure_type, ensure_value = get_cell_ensure_condition(get_cell_value(ws, 't', idx))
                new_foc.bg_insurance_type = ensure_type
                new_foc.bg_insurance_value = ensure_value
                new_foc.bg_bank_account_opening_required = get_cell_bool(get_cell_value(ws, 'u', idx))
            except Exception:
                logger.warning("Error on parsing line {}, finance organization {}".format(idx, bank_name))

            from marer.models.finance_org import FinanceOrganization
            try:
                finance_org = FinanceOrganization.objects.get(name__iexact=bank_name)
            except ObjectDoesNotExist:
                finance_org = FinanceOrganization(name=bank_name)
                finance_org.save()

            new_foc.finance_org = finance_org
            new_foc.finance_product = self.name
            new_foc.save()
            idx += 1
            bank_name = get_cell_value(ws, 'a', idx).value


class CreditProduct(FinanceProduct):
    _humanized_name = 'Кредит'
    _survey_template_name = 'marer/products/Credit/form_survey.html'

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

            self._issue.issuer_head_org_position_and_permissions = form_org_head.cleaned_data[
                'issuer_head_org_position_and_permissions']
            self._issue.issuer_head_phone = form_org_head.cleaned_data['issuer_head_phone']

            self._issue.issuer_head_passport_series = form_org_head.cleaned_data['issuer_head_passport_series']
            self._issue.issuer_head_passport_number = form_org_head.cleaned_data['issuer_head_passport_number']
            self._issue.issuer_head_passport_issue_date = form_org_head.cleaned_data['issuer_head_passport_issue_date']
            self._issue.issuer_head_passport_issued_by = form_org_head.cleaned_data['issuer_head_passport_issued_by']
            self._issue.issuer_head_residence_address = form_org_head.cleaned_data['issuer_head_residence_address']

            self._issue.issuer_head_education_level = form_org_head.cleaned_data['issuer_head_education_level']
            self._issue.issuer_head_org_work_experience = form_org_head.cleaned_data['issuer_head_org_work_experience']
            self._issue.issuer_head_share_in_authorized_capital = form_org_head.cleaned_data[
                'issuer_head_share_in_authorized_capital']
            self._issue.issuer_head_industry_work_experience = form_org_head.cleaned_data[
                'issuer_head_industry_work_experience']
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

        # processing pledge
        from marer.models.issue import IssueCreditPledge
        pledge_formset = formset_factory(CreditPledgeForm, extra=0)
        pld_formset = pledge_formset(request.POST, prefix='pledges')
        if pld_formset.is_valid():
            for pdata in pld_formset.cleaned_data:
                pdata_id = pdata.get('id', None)
                pdata_title = str(pdata.get('pledge_title', '')).strip()
                if pdata_id and pdata.get('DELETE', False):
                    pass
                    try:
                        pldg = IssueCreditPledge.objects.get(id=pdata['id'], issue=self._issue)
                        pldg.delete()
                    except ObjectDoesNotExist:
                        pass  # nothing to do

                elif not pdata_id and pdata_title != '':
                    new_pldg = IssueCreditPledge()
                    new_pldg.pledge_title = pdata_title
                    new_pldg.pledge_type = pdata.get('pledge_type', '')
                    new_pldg.cost = pdata.get('cost', '')
                    new_pldg.issue = self._issue
                    new_pldg.save()

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

    def get_admin_issue_fieldset(self):
        return [
            ('Сведения об истребуемом кредитном продукте', dict(fields=(
                'credit_product_is_credit',
                'credit_product_is_credit_line',
                'credit_product_is_overdraft',

                ('bg_sum', 'bg_currency',),
                'credit_product_interest_rate',
                'credit_repayment_schedule',

                'credit_product_term',
                'credit_product_cl_tranche_term',

                'credit_purpose',
                'credit_repayment_sources',
            ))),

            _admin_issue_fieldset_issuer_part,
            _admin_issue_fieldset_issuer_head_part,
        ]  # todo add fieldsets gathering

    def get_survey_context_part(self):
        affiliates_formset = formset_factory(AffiliatesForm, extra=0)
        from marer.models.issue import IssueBGProdAffiliate
        affiliates = IssueBGProdAffiliate.objects.filter(issue=self._issue)
        affiliates_formset = affiliates_formset(initial=[aff.__dict__ for aff in affiliates], prefix='aff')

        formset_pledges = formset_factory(CreditPledgeForm, extra=0)
        from marer.models.issue import IssueCreditPledge
        pledges = IssueCreditPledge.objects.filter(issue=self._issue)
        formset_pledges = formset_pledges(initial=[p.__dict__ for p in pledges], prefix='pledges')

        formset_founders_legal = formset_factory(FounderLegalForm, extra=0)
        from marer.models.issue import IssueBGProdFounderLegal
        founders_legal = IssueBGProdFounderLegal.objects.filter(issue=self._issue)
        formset_founders_legal = formset_founders_legal(
            initial=[fl.__dict__ for fl in founders_legal],
            prefix='founders_legal'
        )

        formset_founders_physical = formset_factory(FounderPhysicalForm, extra=0)
        from marer.models.issue import IssueBGProdFounderPhysical
        founders_physical = IssueBGProdFounderPhysical.objects.filter(issue=self._issue)
        formset_founders_physical = formset_founders_physical(
            initial=[fp.__dict__ for fp in founders_physical],
            prefix='founders_physical'
        )

        return dict(
            form_org_common=BGFinProdSurveyOrgCommonForm(initial=self._issue.__dict__),
            form_org_head=BGFinProdSurveyOrgHeadForm(initial=self._issue.__dict__),
            affiliates_formset=affiliates_formset,
            formset_pledges=formset_pledges,
            formset_founders_legal=formset_founders_legal,
            formset_founders_physical=formset_founders_physical,
        )

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

            fpdi_code, fpdi_name = _build_accounting_report_common_doc_code_and_name_by_next_quarter_start_date(
                quarters_curr_date)

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

    def get_registering_form_class(self):
        return CreditFinProdRegForm

    def get_finance_orgs_conditions_list_fields(self):
        return [
            ('credit_interest_rate', 'Процентная ставка'),
            ('humanized_bg_insurance', 'Обеспечение'),
            ('humanized_bg_review_tern_days', 'Срок рассмотрения'),
            ('humanized_bg_bank_account_opening_required', 'Открытие р/с'),
            ('humanized_bg_personal_presence_required', 'Личное присутствие'),
        ]

    def get_finance_orgs_conditions_list(self):
        from marer.models.finance_org import FinanceOrgProductConditions
        return FinanceOrgProductConditions.objects.filter(
            finance_product=self.name,
            bg_review_term_days__gt=0,
            credit_interest_rate__gt=0,
        )

    def load_finance_orgs_conditions_from_worksheet(self, ws):
        """
        HEADERS

            coming soon...
        """
        idx = 4

        bank_name = get_cell_value(ws, 'a', idx).value
        while bank_name is not None and bank_name != '':

            from marer.models.finance_org import FinanceOrgProductConditions
            new_foc = FinanceOrgProductConditions()

            try:
                min_sum, max_sum = get_cell_summ_range(get_cell_value(ws, 'b', idx))
                new_foc.credit_min_sum = min_sum
                new_foc.credit_max_sum = max_sum
                new_foc.credit_interest_rate = get_cell_percentage(get_cell_value(ws, 'c', idx))

                # Base conditions
                new_foc.personal_presence_required = get_cell_bool(get_cell_value(ws, 't', idx))
                new_foc.bg_review_term_days = get_cell_review_term_days(get_cell_value(ws, 'u', idx))

                ensure_type, ensure_value = get_cell_ensure_condition(get_cell_value(ws, 'v', idx))
                new_foc.bg_insurance_type = ensure_type
                new_foc.bg_insurance_value = ensure_value
                new_foc.bg_bank_account_opening_required = get_cell_bool(get_cell_value(ws, 'w', idx))
            except Exception:
                logger.warning("Error on parsing line {}, finance organization {}".format(idx, bank_name))

            from marer.models.finance_org import FinanceOrganization
            try:
                finance_org = FinanceOrganization.objects.get(name__iexact=bank_name)
            except ObjectDoesNotExist:
                finance_org = FinanceOrganization(name=bank_name)
                finance_org.save()

            new_foc.finance_org = finance_org
            new_foc.finance_product = self.name
            new_foc.save()
            idx += 1
            bank_name = get_cell_value(ws, 'a', idx).value


class LeasingProduct(FinanceProduct):
    def process_survey_post_data(self, request):
        warnings.warn("Method is not implemented")

    def get_admin_issue_fieldset(self):
        warnings.warn("Method is not implemented")
        return []

    def get_survey_context_part(self):
        warnings.warn("Method is not implemented")
        return dict()

    def process_registering_form(self, request):
        warnings.warn("Method is not implemented")

    _humanized_name = 'Лизинг'

    def get_documents_list(self):
        warnings.warn("Method is not implemented")
        return []

    def get_registering_form_class(self):
        warnings.warn("Method is not implemented")
        return Form

    def get_finance_orgs_conditions_list_fields(self):
        return [
            ('leasing_interest_rate', 'Процентная ставка'),
            ('humanized_bg_insurance', 'Обеспечение'),
            ('humanized_bg_review_tern_days', 'Срок рассмотрения'),
            ('humanized_bg_bank_account_opening_required', 'Открытие р/с'),
            ('humanized_bg_personal_presence_required', 'Личное присутствие'),
        ]

    def get_finance_orgs_conditions_list(self):
        from marer.models.finance_org import FinanceOrgProductConditions
        return FinanceOrgProductConditions.objects.filter(
            finance_product=self.name,
            bg_review_term_days__gt=0,
            leasing_interest_rate__gt=0,
        )

    def load_finance_orgs_conditions_from_worksheet(self, ws):
        warnings.warn("Method is not implemented")
