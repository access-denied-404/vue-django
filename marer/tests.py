from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from marer.models import Issue
from marer.utils.issue import CalculateUnderwritingCriteria


class IssueTestCase(TestCase):

    def test_underwriting_criteria(self):
        issue = Issue()

        # SECTION 1

        issue.bg_sum = 80000
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 100)

        issue.bg_sum = 80000.01
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 75)

        issue.bg_sum = 100000
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 75)

        issue.bg_sum = 100000.01
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 50)

        issue.bg_sum = 150000
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 50)

        issue.bg_sum = 150000.01
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 25)

        issue.bg_sum = 200000
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 25)

        issue.bg_sum = 200000.01
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_1'], 0)

        # SECTION 2

        issue.tender_final_cost = 100000
        issue.balance_code_2110_offset_1 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_2'], 200)

        issue.tender_final_cost = 100000.01
        issue.balance_code_2110_offset_1 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_2'], 100)

        issue.tender_final_cost = 150000
        issue.balance_code_2110_offset_1 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_2'], 100)

        issue.tender_final_cost = 150000.01
        issue.balance_code_2110_offset_1 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_2'], 50)

        issue.tender_final_cost = 200000
        issue.balance_code_2110_offset_1 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_2'], 50)

        issue.tender_final_cost = 200000.01
        issue.balance_code_2110_offset_1 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_2'], 0)

        # SECTION 3

        issue.balance_code_2110_offset_1 = 70
        issue.balance_code_2110_offset_2 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_3'], 50)

        issue.balance_code_2110_offset_1 = 69
        issue.balance_code_2110_offset_2 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_3'], 37.5)

        issue.balance_code_2110_offset_1 = 50
        issue.balance_code_2110_offset_2 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_3'], 37.5)

        issue.balance_code_2110_offset_1 = 49
        issue.balance_code_2110_offset_2 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_3'], 25)

        issue.balance_code_2110_offset_1 = 25
        issue.balance_code_2110_offset_2 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_3'], 25)

        issue.balance_code_2110_offset_1 = 24
        issue.balance_code_2110_offset_2 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_3'], 0)

        # SECTION 4

        issue.balance_code_2110_offset_0 = 70
        issue.balance_code_2110_analog_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_4'], 50)

        issue.balance_code_2110_offset_0 = 69
        issue.balance_code_2110_analog_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_4'], 37.5)

        issue.balance_code_2110_offset_0 = 50
        issue.balance_code_2110_analog_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_4'], 37.5)

        issue.balance_code_2110_offset_0 = 49
        issue.balance_code_2110_analog_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_4'], 25)

        issue.balance_code_2110_offset_0 = 25
        issue.balance_code_2110_analog_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_4'], 25)

        issue.balance_code_2110_offset_0 = 24
        issue.balance_code_2110_analog_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_4'], 0)

        # SECTION 5.1

        issue.bg_sum = 10000000
        issue.tender_final_cost = 150
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 200)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 150.01
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 150)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 200
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 150)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 200.01
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 50)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 400
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 50)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 400.01
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 0)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 0
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 0)

        # SECTION 5.2

        issue.bg_sum = 18000000
        issue.tender_final_cost = 130
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 200)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 130.01
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 130)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 200
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 130)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 200.01
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 20)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 300
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 20)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 300.01
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 0)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 0
        issue.similar_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_51'] + data['score_52'], 0)

        # SECTION 6

        issue.similar_contract_date = (timezone.now() - timezone.timedelta(days=(365*2))).date()
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_6'], 125)

        issue.similar_contract_date = (timezone.now() - timezone.timedelta(days=(365*2 + 1))).date()
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_6'], 62.5)

        issue.similar_contract_date = (timezone.now() - timezone.timedelta(days=(365*3))).date()
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_6'], 62.5)

        issue.similar_contract_date = (timezone.now() - timezone.timedelta(days=(365*3 + 1))).date()
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_6'], 0)

        # SECTION 7.1

        issue.bg_sum = 10000000
        issue.tender_final_cost = 150
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 125)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 150.01
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 93.75)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 200
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 93.75)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 200.01
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 31.25)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 400
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 31.25)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 400.01
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 0)

        issue.bg_sum = 10000000
        issue.tender_final_cost = 0
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 0)

        # SECTION 7.2

        issue.bg_sum = 18000000
        issue.tender_final_cost = 130
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 125)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 130.01
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 81.25)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 200
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 81.25)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 200.01
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 12.5)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 300
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 12.5)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 300.01
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 0)

        issue.bg_sum = 18000000
        issue.tender_final_cost = 0
        issue.biggest_contract_sum = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_71'] + data['score_72'], 0)

        # SECTION 8

        issue.bg_sum = 100
        issue.tender_final_cost = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_8'], 50)

        issue.bg_sum = 100.01
        issue.tender_final_cost = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_8'], 0)

        # SECTION 9

        issue.has_fines_on_zakupki_gov_ru = False
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_9'], 25)

        issue.has_fines_on_zakupki_gov_ru = True
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_9'], 0)

        # SECTION 10

        issue.has_arbitration = False
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_10'], 25)

        issue.has_arbitration = True
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_10'], 0)

        # SECTION 11

        issue.balance_code_1230_offset_0 = 70
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_11'], 50)

        issue.balance_code_1230_offset_0 = 70.01
        issue.balance_code_1600_offset_0 = 100
        data = CalculateUnderwritingCriteria().calc(issue)
        self.assertEqual(data['score_11'], 0)
