import logging
import warnings

from dateutil import parser
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.forms import formset_factory
from django.forms.forms import Form
from django.utils import timezone

from marer import consts
from marer.products.base import FinanceProduct, FinanceProductDocumentItem
from marer.products.forms import BGFinProdRegForm, BGFinProdSurveyOrgCommonForm, BGFinProdSurveyOrgHeadForm, \
    AffiliatesForm, FounderLegalForm, FounderPhysicalForm, CreditFinProdRegForm, CreditPledgeForm, \
    FactoringFinProdRegForm, LeasingFinProdRegForm, LeasingAssetForm, LeasingSupplierForm, LeasingPayRuleForm, \
    FactoringBuyerForm, FactoringSalesAnalyzeForm, BGFinProdSurveyOrgManagementForm, \
    OrgBeneficiaryOwnerForm, OrgBankAccountForm, BGFinProdSurveyDealParamsForm
from marer.utils import kontur
from marer.utils.loadfoc import get_cell_value, get_cell_summ_range, get_cell_percentage, get_cell_bool, \
    get_cell_review_term_days, get_cell_ensure_condition, get_issue_and_interest_rates

logger = logging.getLogger('django')

_admin_issue_fieldset_issuer_part = (
    'Сведения о компании-заявителе',
    dict(
        classes=('collapse',),
        fields=(
            'issuer_short_name',
            'issuer_full_name',
            'issuer_foreign_name',
            'issuer_ogrn',
            'issuer_inn',
            'issuer_kpp',
            'issuer_legal_address',
            'issuer_fact_address',

            'issuer_okpo',
            'issuer_okato',
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

        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_COMMERCIAL:
            docs.extend([
                FinanceProductDocumentItem(
                    code='commerce_tender_contract_for_issue'.format(self._issue.id),
                    name='Скан контракта',
                    description='Отсканированные страницы контракта или его проекта',
                ),
            ])

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

    def process_registering_form(self, request):

        inn = request.POST.get('issuer_inn', None)
        ogrn = request.POST.get('issuer_ogrn', None)

        inn_should_be_requested = inn is not None and inn != self._issue.issuer_inn
        ogrn_should_should_be_requested = ogrn is not None and ogrn != self._issue.issuer_ogrn

        processed_valid = super().process_registering_form(request)

        if inn_should_be_requested or ogrn_should_should_be_requested:
            self._issue.refresh_from_db()
            kontur_req_data = kontur.req(inn=inn, ogrn=ogrn)
            kontur_egrDetails_data = kontur.egrDetails(inn=inn, ogrn=ogrn)
            kontur_beneficialOwners = kontur.beneficialOwners(inn=inn, ogrn=ogrn)
            kontur_licences = kontur.licences(inn=inn, ogrn=ogrn)

            self._issue.issuer_registration_date = parser.parse(kontur_req_data['UL']['registrationDate'] if 'UL' in kontur_req_data else kontur_req_data['IP']['registrationDate'])
            self._issue.issuer_ifns_reg_date = parser.parse(kontur_egrDetails_data['UL']['nalogRegBody']['nalogRegDate'] if 'UL' in kontur_egrDetails_data else kontur_egrDetails_data['IP']['nalogRegBody']['nalogRegDate']).date()
            self._issue.issuer_okopf = kontur_req_data['UL']['okopf'] if 'UL' in kontur_req_data else kontur_req_data['IP']['okopf']
            self._issue.issuer_okpo = kontur_req_data['UL'].get('okpo', '') if 'UL' in kontur_req_data else kontur_req_data['IP'].get('okpo', '')

            if 'UL' in kontur_req_data and len(kontur_req_data['UL']['heads']) > 0:
                head_name_arr = kontur_req_data['UL']['heads'][0]['fio'].split(' ')
                if len(head_name_arr) == 3:
                    self._issue.issuer_head_last_name = head_name_arr[0]
                    self._issue.issuer_head_first_name = head_name_arr[1]
                    self._issue.issuer_head_middle_name = head_name_arr[2]
                self._issue.issuer_head_org_position_and_permissions = kontur_req_data['UL']['heads'][0]['position']
            elif 'IP' in kontur_req_data:
                head_name_arr = kontur_req_data['IP']['fio'].split(' ')
                if len(head_name_arr) == 3:
                    self._issue.issuer_head_last_name = head_name_arr[0]
                    self._issue.issuer_head_first_name = head_name_arr[1]
                    self._issue.issuer_head_middle_name = head_name_arr[2]

            from marer.models.issue import IssueBGProdFounderLegal
            founders_legal = IssueBGProdFounderLegal.objects.filter(issue=self._issue)
            founders_legal.delete()
            if 'UL' in kontur_egrDetails_data:
                for fndr in kontur_egrDetails_data['UL'].get('foundersUL', []):
                    new_fndr = IssueBGProdFounderLegal()
                    new_fndr.issue = self._issue
                    new_fndr.name = fndr['fullName']
                    new_fndr.auth_capital_percentage = str(fndr['share']['percentagePlain']) + '%' if fndr['share'].get('percentagePlain', None) else (str(fndr['share']['sum']) + ' руб.')
                    new_fndr.save()

            from marer.models.issue import IssueBGProdFounderPhysical
            founders_physical = IssueBGProdFounderPhysical.objects.filter(issue=self._issue)
            founders_physical.delete()
            if 'UL' in kontur_egrDetails_data:
                for fndr in kontur_egrDetails_data['UL'].get('foundersFL', []):
                    new_fndr = IssueBGProdFounderPhysical()
                    new_fndr.issue = self._issue
                    new_fndr.fio = fndr['fio']
                    new_fndr.auth_capital_percentage = str(fndr['share']['percentagePlain']) + '%' if fndr['share'].get('percentagePlain', None) else (str(fndr['share']['sum']) + ' руб.')
                    new_fndr.save()

            from marer.models.issue import IssueOrgBeneficiaryOwner
            b_owners = IssueOrgBeneficiaryOwner.objects.filter(issue=self._issue)
            b_owners.delete()
            b_owners_fl = list(kontur_beneficialOwners['beneficialOwners'].get('beneficialOwnersFL', []))
            b_owners_fl.sort(key=lambda x: x.get('share', 0), reverse=True)
            for b_owner in b_owners_fl:
                new_bo = IssueOrgBeneficiaryOwner()
                new_bo.issue = self._issue
                new_bo.fio = b_owner['fio']
                new_bo.inn_or_snils = b_owner.get('innfl', '')
                new_bo.save()

            from marer.models.issue import IssuerLicences
            licences = IssuerLicences.objects.filter(issue=self._issue)
            licences.delete()
            licences_data = list(kontur_licences.get('licenses', []))
            for data in licences_data:
                active = data.get('statusDescription') == 'Действующая'
                if active:
                    number = data.get('officialNum')
                    activity = data.get('activity', '\n'.join(data.get('services', [])))
                    IssuerLicences.objects.create(
                        issue=self._issue,
                        number=number,
                        activity=activity,
                        date_from=data.get('dateStart'),
                        date_to=data.get('dateEnd'),
                    )

            self._issue.save()
        return processed_valid

    def get_survey_context_part(self):
        beneficiary_owners_formset = formset_factory(OrgBeneficiaryOwnerForm, extra=0)
        from marer.models.issue import IssueOrgBeneficiaryOwner
        b_owners = IssueOrgBeneficiaryOwner.objects.filter(issue=self._issue).order_by('id')
        beneficiary_owners_formset = beneficiary_owners_formset(initial=[bo.__dict__ for bo in b_owners], prefix='bo')

        bank_accounts_formset = formset_factory(OrgBankAccountForm, extra=0)
        from marer.models.issue import IssueOrgBankAccount
        b_accounts = IssueOrgBankAccount.objects.filter(issue=self._issue).order_by('id')
        bank_accounts_formset = bank_accounts_formset(initial=[ba.__dict__ for ba in b_accounts], prefix='ba')

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

        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_COMMERCIAL:
            formset_pledges = formset_factory(CreditPledgeForm, extra=0)
            from marer.models.issue import IssueCreditPledge
            pledges = IssueCreditPledge.objects.filter(issue=self._issue)
            formset_pledges = formset_pledges(initial=[p.__dict__ for p in pledges], prefix='pledges')
        else:
            formset_pledges = None

        return dict(
            form_org_common=BGFinProdSurveyOrgCommonForm(initial=self._issue.__dict__),
            form_org_head=BGFinProdSurveyOrgHeadForm(initial=self._issue.__dict__),
            form_org_management=BGFinProdSurveyOrgManagementForm(initial=self._issue.__dict__),
            form_deal_params=BGFinProdSurveyDealParamsForm(initial=self._issue.__dict__),
            bank_accounts_formset=bank_accounts_formset,
            beneficiary_owners_formset=beneficiary_owners_formset,
            formset_founders_legal=formset_founders_legal,
            formset_founders_physical=formset_founders_physical,
            formset_pledges=formset_pledges,
            issue=self._issue,
            consts=consts,
        )

    def process_survey_post_data(self, request):
        processed_sucessfully_flag = True
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

            self._issue.avg_employees_cnt_for_prev_year = form_org_common.cleaned_data['avg_employees_cnt_for_prev_year']
            self._issue.issuer_web_site = form_org_common.cleaned_data['issuer_web_site']
            self._issue.issuer_accountant_org_or_person = form_org_common.cleaned_data['issuer_accountant_org_or_person']
            self._issue.issuer_post_address = form_org_common.cleaned_data['issuer_post_address']
            self._issue.issuer_has_overdue_debts_for_last_180_days = form_org_common.cleaned_data['issuer_has_overdue_debts_for_last_180_days']
            self._issue.issuer_overdue_debts_info = form_org_common.cleaned_data['issuer_overdue_debts_info']

        else:
            processed_sucessfully_flag = False

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
        else:
            processed_sucessfully_flag = False

        form_org_management = BGFinProdSurveyOrgManagementForm(request.POST)
        if form_org_management.is_valid():
            self._issue.issuer_org_management_collegial_executive_name = form_org_management.cleaned_data['issuer_org_management_collegial_executive_name'] or ''
            self._issue.issuer_org_management_collegial_executive_fio = form_org_management.cleaned_data['issuer_org_management_collegial_executive_fio'] or ''
            self._issue.issuer_org_management_directors_or_supervisory_board_name = form_org_management.cleaned_data['issuer_org_management_directors_or_supervisory_board_name'] or ''
            self._issue.issuer_org_management_directors_or_supervisory_board_fio = form_org_management.cleaned_data['issuer_org_management_directors_or_supervisory_board_fio'] or ''
            self._issue.issuer_org_management_other_name = form_org_management.cleaned_data['issuer_org_management_other_name'] or ''
            self._issue.issuer_org_management_other_fio = form_org_management.cleaned_data['issuer_org_management_other_fio'] or ''
        else:
            processed_sucessfully_flag = False

        form_deal_params = BGFinProdSurveyDealParamsForm(request.POST)
        if form_deal_params.is_valid():

            self._issue.bg_is_benefeciary_form = form_deal_params.cleaned_data['bg_is_benefeciary_form']
            self._issue.is_indisputable_charge_off = form_deal_params.cleaned_data['is_indisputable_charge_off']
            self._issue.tender_contract_subject = form_deal_params.cleaned_data['tender_contract_subject']
            self._issue.deal_has_beneficiary = form_deal_params.cleaned_data['deal_has_beneficiary']

            self._issue.issuer_bank_relations_term = form_deal_params.cleaned_data['issuer_bank_relations_term']
            self._issue.issuer_activity_objective = form_deal_params.cleaned_data['issuer_activity_objective']
            self._issue.issuer_finance_situation = form_deal_params.cleaned_data['issuer_finance_situation']
            self._issue.issuer_business_reputation = form_deal_params.cleaned_data['issuer_business_reputation']
            self._issue.issuer_funds_source = form_deal_params.cleaned_data['issuer_funds_source']

        else:
            processed_sucessfully_flag = False

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
        else:
            processed_sucessfully_flag = False

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
        else:
            processed_sucessfully_flag = False

        # processing beneficiary owners
        from marer.models.issue import IssueOrgBeneficiaryOwner
        bo_formset = formset_factory(OrgBeneficiaryOwnerForm, extra=0)
        bo_formset = bo_formset(request.POST, prefix='bo')
        if bo_formset.is_valid():
            for bo_data in bo_formset.cleaned_data:
                bo_data_id = bo_data.get('id', None)
                bo_data_fio = str(bo_data.get('fio', '')).strip()
                if bo_data_id and bo_data.get('DELETE', False):
                    try:
                        aff = IssueOrgBeneficiaryOwner.objects.get(id=bo_data['id'], issue=self._issue)
                        aff.delete()
                    except ObjectDoesNotExist:
                        pass  # nothing to do

                elif not bo_data_id and bo_data_fio != '':
                    new_bo = IssueOrgBeneficiaryOwner()
                    new_bo.fio = bo_data_fio
                    new_bo.legal_address = bo_data.get('legal_address', '')
                    new_bo.fact_address = bo_data.get('fact_address', '')
                    new_bo.post_address = bo_data.get('post_address', '')
                    new_bo.inn_or_snils = bo_data.get('inn_or_snils', '')
                    new_bo.on_belong_to_pub_persons_info = bo_data.get('on_belong_to_pub_persons_info', '')
                    new_bo.issue = self._issue
                    new_bo.save()
        else:
            processed_sucessfully_flag = False

        # processing banks accounts
        from marer.models.issue import IssueOrgBankAccount
        ba_formset = formset_factory(OrgBankAccountForm, extra=0)
        ba_formset = ba_formset(request.POST, prefix='ba')
        if ba_formset.is_valid():
            for ba_data in ba_formset.cleaned_data:
                ba_data_id = ba_data.get('id', None)
                ba_data_name = str(ba_data.get('name', '')).strip()
                if ba_data_id and ba_data.get('DELETE', False):
                    try:
                        aff = IssueOrgBankAccount.objects.get(id=ba_data['id'], issue=self._issue)
                        aff.delete()
                    except ObjectDoesNotExist:
                        pass  # nothing to do

                elif not ba_data_id and ba_data_name != '':
                    new_ba = IssueOrgBankAccount()
                    new_ba.name = ba_data_name
                    new_ba.bik = ba_data.get('bik', '')
                    new_ba.issue = self._issue
                    new_ba.save()
        else:
            processed_sucessfully_flag = False

        # processing pledge
        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_COMMERCIAL:
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
            else:
                processed_sucessfully_flag = False

        return processed_sucessfully_flag

    def get_admin_issue_fieldset(self):
        fieldset = [
            ('Сведения об истребуемой гарантии', dict(fields=(
                ('bg_sum', 'bg_currency',),
                ('bg_start_date', 'bg_end_date',),
                'bg_deadline_date',
                ('tender_exec_law', 'bg_type',),
                'application_doc_admin_field',
                'doc_ops_mgmt_conclusion_doc_admin_field',
                'sec_dep_conclusion_doc_admin_field',
            ))),

            ('Сведения о тендере', dict(classes=('collapse',), fields=(
                'tender_gos_number',
                'tender_gos_number_link',
                'tender_placement_type',
                'tender_publish_date',
                'tender_start_cost',
                'tender_contract_type',
                'tender_has_prepayment',
            ))),

            _admin_issue_fieldset_issuer_part,
            _admin_issue_fieldset_issuer_head_part,

        ]

        tender_responsible_fields_part = (
            'tender_responsible_full_name',
            'tender_responsible_legal_address',
            'tender_responsible_ogrn',
            'tender_responsible_inn',
            'tender_responsible_kpp',
        )

        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_COMMERCIAL:
            fieldset.extend([
                ('Сведения о контракте', dict(classes=('collapse',), fields=(
                    'bg_commercial_contract_subject',
                    'bg_commercial_contract_place_of_work',
                    'bg_commercial_contract_sum',
                    'bg_commercial_contract_sign_date',
                    'bg_commercial_contract_end_date',
                ))),

                ('Сведения о заказчике', dict(
                    classes=('collapse',),
                    fields=tender_responsible_fields_part
                )),
            ])
        else:
            fieldset.extend([
                ('Сведения об организаторе тендера', dict(
                    classes=('collapse',),
                    fields=tender_responsible_fields_part
                )),
            ])

        return fieldset

    def get_admin_issue_read_only_fields(self):
        return [
            'application_doc_admin_field',
            'doc_ops_mgmt_conclusion_doc_admin_field',
            'sec_dep_conclusion_doc_admin_field',
            'tender_gos_number_link',
        ]

    def get_admin_issue_inlnes(self):
        from marer.admin import IssueBGProdAffiliateInlineAdmin
        from marer.admin import IssueBGProdFounderLegalInlineAdmin
        from marer.admin import IssueBGProdFounderPhysicalInlineAdmin
        from marer.admin.inline import IssueCreditPledgeInlineAdmin
        from marer.admin.inline import IssueLicencesInlineAdmin
        inlines = [
            IssueBGProdFounderLegalInlineAdmin,
            IssueBGProdFounderPhysicalInlineAdmin,
            IssueBGProdAffiliateInlineAdmin,
            IssueLicencesInlineAdmin
        ]
        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_COMMERCIAL:
            inlines.append(IssueCreditPledgeInlineAdmin)
        return inlines

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
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_185_FZ:
            interest_rate_field_name = 'bg_185_interest_rate'
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_COMMERCIAL:
            interest_rate_field_name = 'bg_ct_interest_rate'
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_CUSTOMS:
            interest_rate_field_name = 'bg_customs_interest_rate'
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_VAT:
            interest_rate_field_name = 'bg_vat_interest_rate'

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
        final_qs = FinanceOrgProductConditions.objects.none()

        if self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_44_FZ:
            if self._issue.bg_type == consts.BG_TYPE_APPLICATION_ENSURE:
                final_qs = qs.filter(
                    Q(Q(bg_44_app_ensure_min_sum__lte=self._issue.sum_not_null)
                      | Q(bg_44_app_ensure_min_sum__isnull=True)),
                    Q(Q(bg_44_app_ensure_max_sum__gt=self._issue.sum_not_null)
                      | Q(bg_44_app_ensure_max_sum__isnull=True)),
                    bg_44_app_ensure_interest_rate__isnull=False
                )
            elif self._issue.bg_type == consts.BG_TYPE_CONTRACT_EXECUTION:
                final_qs = qs.filter(
                    Q(Q(bg_44_contract_exec_min_sum__lte=self._issue.sum_not_null)
                      | Q(bg_44_contract_exec_min_sum__isnull=True)),
                    Q(Q(bg_44_contract_exec_max_sum__gt=self._issue.sum_not_null)
                      | Q(bg_44_contract_exec_max_sum__isnull=True)),
                    bg_44_contract_exec_interest_rate__isnull=False
                )
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_223_FZ:
            if self._issue.bg_type == consts.BG_TYPE_APPLICATION_ENSURE:
                final_qs = qs.filter(
                    Q(Q(bg_223_app_ensure_min_sum__lte=self._issue.sum_not_null)
                      | Q(bg_223_app_ensure_min_sum__isnull=True)),
                    Q(Q(bg_223_app_ensure_max_sum__gt=self._issue.sum_not_null)
                      | Q(bg_223_app_ensure_max_sum__isnull=True)),
                    bg_223_app_ensure_interest_rate__isnull=False
                )
            elif self._issue.bg_type == consts.BG_TYPE_CONTRACT_EXECUTION:
                final_qs = qs.filter(
                    Q(Q(bg_223_contract_exec_min_sum__lte=self._issue.sum_not_null)
                      | Q(bg_223_contract_exec_min_sum__isnull=True)),
                    Q(Q(bg_223_contract_exec_max_sum__gt=self._issue.sum_not_null)
                      | Q(bg_223_contract_exec_max_sum__isnull=True)),
                    bg_223_contract_exec_interest_rate__isnull=False
                )
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_185_FZ:
            final_qs = qs.filter(
                Q(Q(bg_185_min_sum__lte=self._issue.sum_not_null)
                  | Q(bg_185_min_sum__isnull=True)),
                Q(Q(bg_185_max_sum__gt=self._issue.sum_not_null)
                  | Q(bg_185_max_sum__isnull=True)),
                bg_185_interest_rate__isnull=False
            )
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_COMMERCIAL:
            final_qs = qs.filter(
                Q(Q(bg_ct_min_sum__lte=self._issue.sum_not_null)
                  | Q(bg_ct_min_sum__isnull=True)),
                Q(Q(bg_ct_max_sum__gt=self._issue.sum_not_null)
                  | Q(bg_ct_max_sum__isnull=True)),
                bg_ct_interest_rate__isnull=False
            )
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_CUSTOMS:
            final_qs = qs.filter(
                Q(Q(bg_customs_min_sum__lte=self._issue.sum_not_null)
                  | Q(bg_customs_min_sum__isnull=True)),
                Q(Q(bg_customs_max_sum__gt=self._issue.sum_not_null)
                  | Q(bg_customs_max_sum__isnull=True)),
                bg_customs_interest_rate__isnull=False
            )
        elif self._issue.tender_exec_law == consts.TENDER_EXEC_LAW_VAT:
            final_qs = qs.filter(
                Q(Q(bg_vat_min_sum__lte=self._issue.sum_not_null)
                  | Q(bg_vat_min_sum__isnull=True)),
                Q(Q(bg_vat_max_sum__gt=self._issue.sum_not_null)
                  | Q(bg_vat_max_sum__isnull=True)),
                bg_vat_interest_rate__isnull=False
            )

        return final_qs

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
