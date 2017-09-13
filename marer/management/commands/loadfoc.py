import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from openpyxl import load_workbook

from marer.models.finance_org import FinanceOrgProductConditions, FinanceOrganization
from marer.products import BankGuaranteeProduct

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

        bank_name = self._get_cell_data(sh, 'a', idx).value
        while bank_name is not None and bank_name != '':

            new_foc = FinanceOrgProductConditions()

            try:
                # Subtypes conditions
                # 44-FZ
                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'b', idx))
                new_foc.bg_44_app_ensure_min_sum = min_sum
                new_foc.bg_44_app_ensure_max_sum = max_sum
                new_foc.bg_44_app_ensure_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'c', idx))

                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'd', idx))
                new_foc.bg_44_contract_exec_min_sum = min_sum
                new_foc.bg_44_contract_exec_max_sum = max_sum
                new_foc.bg_44_contract_exec_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'e', idx))

                # 223-FZ
                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'f', idx))
                new_foc.bg_223_app_ensure_min_sum = min_sum
                new_foc.bg_223_app_ensure_max_sum = max_sum
                new_foc.bg_223_app_ensure_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'g', idx))

                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'h', idx))
                new_foc.bg_223_contract_exec_min_sum = min_sum
                new_foc.bg_223_contract_exec_max_sum = max_sum
                new_foc.bg_223_contract_exec_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'i', idx))


                # 185-FZ
                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'j', idx))
                new_foc.bg_185_min_sum = min_sum
                new_foc.bg_185_max_sum = max_sum
                new_foc.bg_185_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'k', idx))

                # Commercial
                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'l', idx))
                new_foc.bg_ct_min_sum = min_sum
                new_foc.bg_ct_max_sum = max_sum
                new_foc.bg_ct_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'm', idx))

                # VAT
                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'n', idx))
                new_foc.bg_vat_min_sum = min_sum
                new_foc.bg_vat_max_sum = max_sum
                new_foc.bg_vat_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'o', idx))

                # Customs
                min_sum, max_sum = self._get_cell_summ_range(self._get_cell_data(sh, 'p', idx))
                new_foc.bg_customs_min_sum = min_sum
                new_foc.bg_customs_max_sum = max_sum
                new_foc.bg_customs_interest_rate = self._get_cell_percentage(self._get_cell_data(sh, 'q', idx))

                # Base conditions
                new_foc.personal_presence_required = self._get_cell_bool(self._get_cell_data(sh, 'r', idx))
                new_foc.bg_review_term_days = self._get_cell_review_term_days(self._get_cell_data(sh, 's', idx))

                ensure_type, ensure_value = self._get_cell_ensure_condition(self._get_cell_data(sh, 't', idx))
                new_foc.bg_insurance_type = ensure_type
                new_foc.bg_insurance_value = ensure_value
                new_foc.bg_bank_account_opening_required = self._get_cell_bool(self._get_cell_data(sh, 'u', idx))
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
            bank_name = self._get_cell_data(sh, 'a', idx).value

    def _get_cell_summ_range(self, cell_data):

        if cell_data.value is None or cell_data.value == '':
            return None, None

        # variants:
        #   ' от ХХХ млн '
        #   ' до ХХХ млн '
        #   ' от ХХХ млн до ХХХ млн'
        #   ' ХХХ млн - ХХХ млн '

        min_sum = None
        max_sum = None

        patterns = [
            re.compile('\s*от\s*(?P<min_sum>\d+)\s*(?P<min_mult>\w*)\s*до\s*(?P<max_sum>\d+)\s*(?P<max_mult>\w*)\s*'),
            re.compile('\s*от\s*(?P<min_sum>\d+)\s*(?P<min_mult>\w*)\s*'),
            re.compile('\s*до\s*(?P<max_sum>\d+)\s*(?P<max_mult>\w*)\s*'),
            re.compile('\s*(?P<min_sum>\d+)\s*(?P<min_mult>\w*)\s*-\s*(?P<max_sum>\d+)\s*(?P<max_mult>\w*)\s*'),
        ]
        for pattern in patterns:
            matches = pattern.fullmatch(str(cell_data.value).lower())
            if matches:
                multipliers = {
                    'тыс': 1000,
                    'млн': 1000000,
                    'млрд': 1000000000,
                }

                match_data = matches.groupdict()

                min_sum = match_data.get('min_sum', None)
                if min_sum is not None:
                    min_mult = multipliers.get(match_data.get('min_mult', None), 1)
                    min_sum = int(min_sum) * min_mult

                max_sum = match_data.get('max_sum', None)
                if max_sum is not None:
                    max_mult = multipliers.get(match_data.get('max_mult', None), 1)
                    max_sum = int(max_sum) * max_mult

                break

        return min_sum, max_sum

    def _get_cell_percentage(self, cell_data):

        if cell_data.value is None or cell_data.value == '':
            return None

        # variants
        #   ' 1,2 % '
        #   ' 2 % '
        #   ' 3.5 % '

        percentage = None

        patterns = [
            re.compile('\s*(?P<int_part>\d+)[.,](?P<decimal_part>\d+)\s*%?\s*'),
            re.compile('\s*(?P<int_part>\d+)\s*%?\s*'),
        ]
        for pattern in patterns:
            matches = pattern.fullmatch(cell_data.value)
            if matches:
                match_data = matches.groupdict()
                percentage = float('{int_part}.{decimal_part}'.format(
                    int_part=match_data.get('int_part', 0),
                    decimal_part=match_data.get('decimal_part', 0),
                ))
                break

        return percentage

    def _get_cell_bool(self, cell_data):

        if cell_data.value is None or cell_data.value == '':
            return False

        # variants
        #   ' да '
        #   ' нет '
        #   ' + '
        #   ' - '

        patterns_true = [
            re.compile('\s*да\s*'),
            re.compile('\s*\+\s*'),
        ]
        patterns_false = [
            re.compile('\s*нет\s*'),
            re.compile('\s*-\s*'),
        ]

        for pattern in patterns_true:
            matches = pattern.fullmatch(str(cell_data.value).lower())
            if matches:
                return True

        for pattern in patterns_false:
            matches = pattern.fullmatch(str(cell_data.value).lower())
            if matches:
                return False

        return False

    def _get_cell_review_term_days(self, cell_data):

        if cell_data.value is None or cell_data.value == '':
            return 0

        # variants
        #   ' 10 '
        #   ' 10 дней '
        #   ' 2 дня '
        #   ' 10 д '
        #   ' 10 дн '
        #   ' 10 дн. '

        pattern = re.compile('\s*(?P<days>\d+)\s*(дней|дня|д|дн|дн.)?\s*')

        matches = pattern.fullmatch(str(cell_data.value).lower())
        if matches:
            days_data = matches.groupdict().get('days', None)
            return int(days_data) if days_data else 0

        return 0

    def _get_cell_ensure_condition(self, cell_data):

        if cell_data.value is None or cell_data.value == '':
            return None, 0

        # variants
        #   ' залог 10 % '
        #   ' 10 % '
        #   ' недвижимость '
        #   ' нет '

        patterns_pledge = [
            re.compile('\s*залог\s*(?P<percentage>\d+)\s*%\s*'),
            re.compile('\s*(?P<percentage>\d+)\s*%\s*'),
        ]
        patterns_estate = [
            re.compile('\s*недвижимость\s*'),
            re.compile('\s*-\s*'),
        ]
        patterns_none = [
            re.compile('\s*нет\s*'),
        ]

        for pattern in patterns_pledge:
            matches = pattern.fullmatch(str(cell_data.value).lower())
            if matches:
                ens_data = matches.groupdict()
                ensure_type = FinanceOrgProductConditions.INSURANCE_TYPE_PLEDGE
                ensure_value = int(ens_data.get('percentage'))
                return ensure_type, ensure_value

        for pattern in patterns_estate:
            matches = pattern.fullmatch(str(cell_data.value).lower())
            if matches:
                return FinanceOrgProductConditions.INSURANCE_TYPE_REAL_ESTATE, 100

        for pattern in patterns_none:
            matches = pattern.fullmatch(str(cell_data.value).lower())
            if matches:
                return None, 0

    def _get_cell_data(self, sheet, col, row):
        sheet_idx = '{col}{row}'.format(col=str(col).upper(), row=row)
        return sheet[sheet_idx]
