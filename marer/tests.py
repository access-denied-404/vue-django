from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from marer.products import BankGuaranteeProduct


class BankGuaranteeProductTestCase(TestCase):

    def test_product_bg_common_documents_codes_list(self):
        arf_y2014q3_y2015q3 = [
            'accounting_report_forms_1_2_for_y2014q3',
            'accounting_report_forms_1_2_for_y2014',
            'accounting_report_forms_1_2_for_y2015q1',
            'accounting_report_forms_1_2_for_y2015q2',
            'accounting_report_forms_1_2_for_y2015q3']

        arf_y2014_y2015 = [
            'accounting_report_forms_1_2_for_y2014',
            'accounting_report_forms_1_2_for_y2015q1',
            'accounting_report_forms_1_2_for_y2015q2',
            'accounting_report_forms_1_2_for_y2015q3',
            'accounting_report_forms_1_2_for_y2015']

        arf_y2015q1_y2016q1 = [
            'accounting_report_forms_1_2_for_y2015q1',
            'accounting_report_forms_1_2_for_y2015q2',
            'accounting_report_forms_1_2_for_y2015q3',
            'accounting_report_forms_1_2_for_y2015',
            'accounting_report_forms_1_2_for_y2016q1']

        arf_y2015q2_y2016q2 = [
            'accounting_report_forms_1_2_for_y2015q2',
            'accounting_report_forms_1_2_for_y2015q3',
            'accounting_report_forms_1_2_for_y2015',
            'accounting_report_forms_1_2_for_y2016q1',
            'accounting_report_forms_1_2_for_y2016q2']

        arf_y2015q3_y2016q3 = [
            'accounting_report_forms_1_2_for_y2015q3',
            'accounting_report_forms_1_2_for_y2015',
            'accounting_report_forms_1_2_for_y2016q1',
            'accounting_report_forms_1_2_for_y2016q2',
            'accounting_report_forms_1_2_for_y2016q3']

        arf_assert_data = {
            1: arf_y2014q3_y2015q3 + ['loans_description_yr2016_m1', 'contracts_registry_yr2016_m1'],
            2: arf_y2014_y2015 + ['loans_description_yr2016_m2', 'contracts_registry_yr2016_m2'],
            3: arf_y2014_y2015 + ['loans_description_yr2016_m3', 'contracts_registry_yr2016_m3'],
            4: arf_y2014_y2015 + ['loans_description_yr2016_m4', 'contracts_registry_yr2016_m4'],
            5: arf_y2015q1_y2016q1 + ['loans_description_yr2016_m5', 'contracts_registry_yr2016_m5'],
            6: arf_y2015q1_y2016q1 + ['loans_description_yr2016_m6', 'contracts_registry_yr2016_m6'],
            7: arf_y2015q1_y2016q1 + ['loans_description_yr2016_m7', 'contracts_registry_yr2016_m7'],
            8: arf_y2015q2_y2016q2 + ['loans_description_yr2016_m8', 'contracts_registry_yr2016_m8'],
            9: arf_y2015q2_y2016q2 + ['loans_description_yr2016_m9', 'contracts_registry_yr2016_m9'],
            10: arf_y2015q2_y2016q2 + ['loans_description_yr2016_m10', 'contracts_registry_yr2016_m10'],
            11: arf_y2015q3_y2016q3 + ['loans_description_yr2016_m11', 'contracts_registry_yr2016_m11'],
            12: arf_y2015q3_y2016q3 + ['loans_description_yr2016_m12', 'contracts_registry_yr2016_m12'],
        }

        product = BankGuaranteeProduct()
        for month_num in arf_assert_data:
            now_override = timezone.localtime(
                timezone.now(),
                timezone.get_current_timezone()
            ).replace(
                year=2016,
                month=month_num,
            )
            common_docs_list = [doc.code for doc in product.get_documents_list(now_override)]
            self.assertListEqual(common_docs_list, arf_assert_data[month_num])
