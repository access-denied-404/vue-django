import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from openpyxl import load_workbook

from marer.models.finance_org import FinanceOrgProductConditions, FinanceOrganization
from marer.products import BankGuaranteeProduct
from marer.utils.loadfoc import get_cell_percentage, get_cell_bool, get_cell_review_term_days, \
    get_cell_ensure_condition, get_cell_summ_range, get_cell_value

logger = logging.getLogger('django')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=str)
        parser.add_argument('sheet', nargs='?', type=str)

    def handle(self, *args, **options):

        product = BankGuaranteeProduct()  # todo set product from params
        filename = options.get('filename')[0]
        sheet_name = options.get('sheet', None)

        foc_list = FinanceOrgProductConditions.objects.filter(finance_product=product.name)
        for foc in foc_list:
            foc.delete()

        wb = load_workbook(filename)
        if sheet_name is not None:
            sh = wb.get_sheet_by_name(sheet_name)
        else:
            sheets = wb.get_sheet_names()
            sh = wb.get_sheet_by_name(sheets[0])

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

        bank_name = get_cell_value(sh, 'a', idx).value
        while bank_name is not None and bank_name != '':

            new_foc = FinanceOrgProductConditions()

            try:
                # Subtypes conditions
                # 44-FZ
                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'b', idx))
                new_foc.bg_44_app_ensure_min_sum = min_sum
                new_foc.bg_44_app_ensure_max_sum = max_sum
                new_foc.bg_44_app_ensure_interest_rate = get_cell_percentage(get_cell_value(sh, 'c', idx))

                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'd', idx))
                new_foc.bg_44_contract_exec_min_sum = min_sum
                new_foc.bg_44_contract_exec_max_sum = max_sum
                new_foc.bg_44_contract_exec_interest_rate = get_cell_percentage(get_cell_value(sh, 'e', idx))

                # 223-FZ
                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'f', idx))
                new_foc.bg_223_app_ensure_min_sum = min_sum
                new_foc.bg_223_app_ensure_max_sum = max_sum
                new_foc.bg_223_app_ensure_interest_rate = get_cell_percentage(get_cell_value(sh, 'g', idx))

                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'h', idx))
                new_foc.bg_223_contract_exec_min_sum = min_sum
                new_foc.bg_223_contract_exec_max_sum = max_sum
                new_foc.bg_223_contract_exec_interest_rate = get_cell_percentage(get_cell_value(sh, 'i', idx))


                # 185-FZ
                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'j', idx))
                new_foc.bg_185_min_sum = min_sum
                new_foc.bg_185_max_sum = max_sum
                new_foc.bg_185_interest_rate = get_cell_percentage(get_cell_value(sh, 'k', idx))

                # Commercial
                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'l', idx))
                new_foc.bg_ct_min_sum = min_sum
                new_foc.bg_ct_max_sum = max_sum
                new_foc.bg_ct_interest_rate = get_cell_percentage(get_cell_value(sh, 'm', idx))

                # VAT
                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'n', idx))
                new_foc.bg_vat_min_sum = min_sum
                new_foc.bg_vat_max_sum = max_sum
                new_foc.bg_vat_interest_rate = get_cell_percentage(get_cell_value(sh, 'o', idx))

                # Customs
                min_sum, max_sum = get_cell_summ_range(get_cell_value(sh, 'p', idx))
                new_foc.bg_customs_min_sum = min_sum
                new_foc.bg_customs_max_sum = max_sum
                new_foc.bg_customs_interest_rate = get_cell_percentage(get_cell_value(sh, 'q', idx))

                # Base conditions
                new_foc.personal_presence_required = get_cell_bool(get_cell_value(sh, 'r', idx))
                new_foc.bg_review_term_days = get_cell_review_term_days(get_cell_value(sh, 's', idx))

                ensure_type, ensure_value = get_cell_ensure_condition(get_cell_value(sh, 't', idx))
                new_foc.bg_insurance_type = ensure_type
                new_foc.bg_insurance_value = ensure_value
                new_foc.bg_bank_account_opening_required = get_cell_bool(get_cell_value(sh, 'u', idx))
            except Exception:
                logger.warning("Error on parsing line {}, finance organization {}".format(idx, bank_name))

            try:
                finance_org = FinanceOrganization.objects.get(name__iexact=bank_name)
            except ObjectDoesNotExist:
                finance_org = FinanceOrganization(name=bank_name)
                finance_org.save()

            new_foc.finance_org = finance_org
            new_foc.finance_product = product.name
            new_foc.save()
            idx += 1
            bank_name = get_cell_value(sh, 'a', idx).value
