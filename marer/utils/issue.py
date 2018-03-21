import os
import math
import zipfile
import io

from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.utils.formats import number_format
from django.utils.timezone import now
from django.conf import settings

from marer import consts
from marer.models import BankMinimalCommission
from marer.utils.datetime_utils import get_datetime_as_excel_number, get_date_diff_in_days


def issue_term_in_months(start_date, end_date):

    def _year(datetime):
        return datetime.year

    def _month(datetime):
        return datetime.month

    if start_date and end_date:
        months = 1 + (_year(end_date) - _year(start_date)) * 12 + _month(end_date) - _month(start_date)
    else:
        months = 0
    return months


def calculate_effective_rate(bg_sum, commission, bg_start_date, bg_end_date):
    """
    Расчет эффективной процентной ставки
    :param bg_sum:
    :param auto_commission:
    :param agent_commission:
    :param bg_start_date:
    :param bg_end_date:
    :return:
    """
    AN10 = get_date_diff_in_days(bg_start_date, bg_end_date)

    Y16 = int(commission) * 100 / int(bg_sum)

    return Y16 / AN10 * 365


def calculate_bank_commission(bg_start_date, bg_end_date, bg_sum, bg_is_beneficiary_form, bg_type, tender_exec_law,
                              tender_has_prepayment, contract_term_extend=False, contract_exec_verification_more_5_doc=False):
    """
    Расчет банковской комиссии
    :param bg_start_date:
    :param bg_end_date:
    :param bg_sum:
    :param bg_is_beneficiary_form:
    :param bg_type:
    :param tender_exec_law:
    :param tender_has_prepayment:
    :param contract_term_extend:
    :param contract_exec_verification_more_5_doc:
    :return:
    """
    Q25 = 0.0027  # Процент: 0,27% (процент чего?)
    M10 = 0.1  # Предоставление гарантии по форме заказчика: 10%
    M11 = 0.1  # Контрактом предусмотрена возможность выплаты Аванса: 10%
    M12 = 0.05  # Гарантия в рамках 185-ФЗ: 5%
    M13 = 0.05  # Гарантия качества: 10%
    M14 = 0.15  # Увеличение/продление срока контракта: 5%
    M15 = 0.05  # Подтверждение опыта исполнения контрактов (более 5 документов): 15%
    M16 = 0  # Сумма БГ более 5 млн.

    E7 = bg_start_date
    F10 = bg_sum
    F11 = bg_end_date
    F17 = bg_is_beneficiary_form
    F18 = tender_has_prepayment
    F19 = tender_exec_law == consts.TENDER_EXEC_LAW_185_FZ  # Гарантия в рамках 185-ФЗ: +/-
    F20 = bg_type == consts.BG_TYPE_WARRANTY_ENSURE
    F21 = contract_exec_verification_more_5_doc  # Подтверждение опыта исполнения контрактов (более 5 документов): +/-
    F22 = contract_term_extend  # Увеличение/продление срока контракта: +/-
    F23 = bg_sum > 5000000

    # F23: **Пусто**
    # M16: **Пусто**
    # M130: **Пусто**

    O25 = issue_term_in_months(E7, F11)
    Q17 = float(F10) * O25 * Q25
    Q22 = Q17 * (
        1
        + (M10 if F17 else 0)
        + (M11 if F18 else 0)
        + (M12 if F19 else 0)
        + (M13 if F20 else 0)
        + (M15 if F21 else 0)
        + (M14 if F22 else 0)
        + (M16 if F23 else 0)
    )
    try:
        min_com = BankMinimalCommission.objects.get(
            sum_min__lte=bg_sum,
            sum_max__gte=bg_sum,
            term_months_min__lte=O25,
            term_months_max__gte=O25,
        )
        O24 = min_com.commission
    except ObjectDoesNotExist:
        return None

    Q20 = O24 if Q22 < O24 else Q22  # Q20: =ЕСЛИ(Q22<O24;O24;Q22)
    return round(Q20, 2)


def generate_bg_number(date):
    prefix = '19/'
    suffix = 'ЭГ-18'
    today = get_datetime_as_excel_number(date)
    part1 = math.floor(today) - 42900
    part2 = math.floor((math.fmod(today, 1) * 100000))
    return '%s%s-%s%s' % (prefix, part1, part2, suffix)


def sum_str_format(value):
    zero = 'ноль'
    ten = (
        ('', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять'),
        ('', 'одна', 'две', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять'),
    )
    a20 = [
        'десять', 'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать', 'пятнадцать',
        'шестнадцать', 'семнадцать', 'восемнадцать', 'девятнадцать'
    ]
    tens = [
        '', '', 'двадцать', 'тридцать', 'сорок', 'пятьдесят', 'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто'
    ]
    hundred = [
        '', 'сто', 'двести', 'триста', 'четыреста', 'пятьсот', 'шестьсот', 'семьсот', 'восемьсот', 'девятьсот'
    ]
    unit = [  # Units
        ['копейка', 'копейки', 'копеек', 1],
        ['рубль', 'рубля', 'рублей', 1],
        ['тысяча', 'тысячи', 'тысяч', 1],
        ['миллион', 'миллиона', 'миллионов', 0],
        ['миллиард', 'милиарда', 'миллиардов', 0],
    ]

    value = str(value).replace(' ', '')
    if '.' in value:
        rub, kop = ('%3.2f' % float(value)).split('.')
    elif ',' in value:
        rub, kop = ('%3.2f' % float(value)).split(',')
    else:
        rub = float(value)
        kop = 0

    digits = []
    currency = []

    def split_by_groups(value: str, count: int):
        value = str(int(value))
        extended_length = len(value) * 1.0 / count
        extended_value = value.rjust(math.ceil(extended_length) * count, '0')
        return [extended_value[i: i + count] for i in range(0, len(extended_value), count)]

    def morph(value, var1, var2, var3):
        value = abs(int(value)) % 100
        if value > 10 and value < 20:
            return var3
        value = value % 10
        if value > 1 and value < 5:
            return var2
        if value == 1:
            return var1
        return var3

    if int(rub) > 0:
        groups = split_by_groups(rub, 3)
        rub_formatted = str(number_format(rub, force_grouping=True))
        for id, group in enumerate(groups):
            i1, i2, i3 = list([int(g) for g in group])
            unit_id = len(groups) - id
            current_unit = unit[unit_id]
            gender = current_unit[3]
            if i1 > 0:
                digits.append(hundred[i1])
            if i2 > 1:
                if i3 != 0:
                    text = tens[i2] + ' ' + ten[gender][i3]
                else:
                    text = tens[i2]  # 20-99
                digits.append(text)
            else:
                if i2 > 0:
                    text = a20[i3]
                else:
                    text = ten[gender][i3]  # 10-19 | 1-9
                digits.append(text)
            if unit_id > 0:
                if id == len(groups) - 1:
                    currency.append(morph(group, *current_unit[:3]))
                elif int(group) > 0:
                    digits.append(morph(group, *current_unit[:3]))
        currency.append(str(kop))
        currency.append(morph(kop, *unit[0][:3]))
    digits_str = ' '.join(digits).strip()
    return rub_formatted + ' (' + digits_str.capitalize() + ') ' + ' '.join(currency).strip()


class CalculateUnderwritingCriteria:

    def score_1(self, value):
        total = 100
        if 80 < value <= 100:
            score = 0.25
        elif 100 < value <= 150:
            score = 0.5
        elif 150 < value <= 200:
            score = 0.75
        elif 200 < value:
            score = 1
        else:
            score = 0
        return total - total * score

    def score_2(self, value):
        total = 200
        if 100 < value <= 150:
            score = 0.5
        elif 150 < value <= 200:
            score = 0.75
        elif 200 < value:
            score = 1
        else:
            score = 0
        return total - total * score

    def score_3(self, value):
        total = 50
        if 30 < value <= 50:
            score = 0.25
        elif 50 < value <= 75:
            score = 0.5
        elif 75 < value <= 100:
            score = 1
        else:
            score = 0
        return total - total * score

    def score_4(self, value):
        return self.score_3(value)

    def score_51(self, value, bg_sum):
        total = 200
        if 1500000 < bg_sum <= 5000000:
            if value == 0:
                score = 1
            elif 2 < value <= 3:
                score = 0.25
            elif 3 < value <= 5:
                score = 0.75
            elif 5 < value:
                score = 1
            else:
                score = 0
            return total - total * score
        return 0

    def score_52(self, value, bg_sum):
        total = 200
        if 5000000 < bg_sum <= 10000000:
            if value == 0:
                score = 1
            elif 1.5 < value <= 2:
                score = 0.25
            elif 2 < value <= 4:
                score = 0.75
            elif 4 < value:
                score = 1
            else:
                score = 0
            return total - total * score
        return 0

    def score_53(self, value, bg_sum):
        total = 200
        if 10000000 < bg_sum <= 18000000:
            if value == 0:
                score = 1
            elif 1.3 < value <= 2:
                score = 0.35
            elif 2 < value <= 3:
                score = 0.9
            elif 3 < value:
                score = 1
            else:
                score = 0
            return total - total * score
        return 0

    def score_6(self, value):
        total = 125

        if 2 < value <= 3:
            score = 0.5
        elif 3 < value:
            score = 1
        else:
            score = 0
        return total - total * score

    def score_71(self, value, bg_sum):
        total = 125
        if 1500000 < bg_sum <= 5000000:
            if value == 0:
                score = 1
            elif 2 < value <= 3:
                score = 0.25
            elif 3 < value <= 5:
                score = 0.75
            elif 5 < value:
                score = 1
            else:
                score = 0
            return total - total * score
        return 0

    def score_72(self, value, bg_sum):
        total = 125
        if 5000000 < bg_sum <= 10000000:
            if value == 0:
                score = 1
            elif 1.5 < value <= 2:
                score = 0.25
            elif 2 < value <= 4:
                score = 0.75
            elif 4 < value:
                score = 1
            else:
                score = 0
            return total - total * score
        return 0

    def score_73(self, value, bg_sum):
        total = 125
        if 10000000 < bg_sum <= 18000000:
            if value == 0:
                score = 1
            elif 1.3 < value <= 2:
                score = 0.35
            elif 2 < value <= 3:
                score = 0.9
            elif 3 < value:
                score = 1
            else:
                score = 0
            return total - total * score
        return 0

    def score_8(self, value):
        total = 50
        return total if value else 0

    def score_9(self, value):
        total = 25
        return total if not value else 0

    def score_10(self, value):
        total = 25
        return total if not value else 0

    def score_11(self, value):
        total = 50
        return total if value <= 70 else 0

    def calc(self, issue):
        float_bg_sum = float(issue.bg_sum)
        bg_sum_thousands = (issue.bg_sum / 1000) if issue.bg_sum else 0
        tender_final_cost_thousands = (issue.tender_final_cost / 1000) if issue.tender_final_cost else 0

        value_1 = (bg_sum_thousands / issue.balance_code_1600_offset_0 * 100) if bg_sum_thousands and issue.balance_code_1600_offset_0 else 0
        value_2 = (tender_final_cost_thousands / issue.balance_code_2110_offset_1 * 100) if issue.balance_code_2110_offset_1 and tender_final_cost_thousands else 0
        value_3 = int((1 - issue.balance_code_2110_offset_1 / issue.balance_code_2110_offset_2) * 100) if issue.balance_code_2110_offset_1 and issue.balance_code_2110_offset_2 else 100
        value_4 = int((1 - issue.balance_code_2110_offset_0 / issue.balance_code_2110_analog_offset_0) * 100) if issue.balance_code_2110_offset_0 and issue.balance_code_2110_analog_offset_0 else 100
        value_5 = (float(issue.tender_final_cost) / issue.similar_contract_sum) if issue.bg_sum and issue.tender_final_cost and issue.similar_contract_sum and issue.similar_contract_sum > 0 else 0
        value_6 = ((now().date() - issue.similar_contract_date).days / 365) if issue.similar_contract_date else 0
        value_7 = (issue.tender_final_cost / Decimal(issue.biggest_contract_sum)) if float_bg_sum and issue.tender_final_cost and issue.biggest_contract_sum and issue.biggest_contract_sum > 0 else 0
        value_8 = (float_bg_sum <= issue.tender_final_cost) if float_bg_sum and issue.tender_final_cost else False
        value_11 = (issue.balance_code_1230_offset_0 / issue.balance_code_1600_offset_0 * 100) if issue.balance_code_1230_offset_0 and issue.balance_code_1600_offset_0 else 0
        data = {
            "value_1": '{:0.2f} %'.format(value_1),
            "score_1": self.score_1(value_1),

            "value_2": '{:0.2f} %'.format(value_2),
            "score_2": self.score_2(value_2),

            "value_3": '{:0.2f} %'.format(value_3),
            "score_3": self.score_3(value_3),

            "value_4": '{:0.2f} %'.format(value_4),
            "score_4": self.score_4(value_4),

            "value_5": '{:0.1f}'.format(value_5),
            "score_51": self.score_51(value_5, issue.bg_sum),
            "score_52": self.score_52(value_5, issue.bg_sum),
            "score_53": self.score_53(value_5, issue.bg_sum),

            "value_6": '{:0.1f}'.format(value_6),
            "score_6": self.score_6(value_6),

            "value_7": '{:0.1f}'.format(value_7),
            "score_71": self.score_71(value_7, issue.bg_sum),
            "score_72": self.score_72(value_7, issue.bg_sum),
            "score_73": self.score_73(value_7, issue.bg_sum),

            "value_8": 'ДА' if value_8 else 'НЕТ',
            "score_8": self.score_8(value_8),

            "value_9": 'ДА' if issue.has_fines_on_zakupki_gov_ru else 'НЕТ',
            "score_9": self.score_9(issue.has_fines_on_zakupki_gov_ru),

            "value_10": 'ДА' if issue.has_arbitration else 'НЕТ',
            "score_10": self.score_10(issue.has_arbitration),

            "value_11": '{:0.2f} %'.format(value_11),
            "score_11": self.score_11(value_11),
        }

        total = 0
        for key, value in data.items():
            if key.startswith('score_'):
                total += value

        data['result'] = total
        return data


def zip_docs(doc_list):
    zip_io = io.BytesIO()

    with zipfile.ZipFile(zip_io, mode='w') as zip:
        for doc in doc_list:
            if doc.document:
                path = doc.document.file.name
                zip.write('media/' + path, arcname=path.split('/')[-1])
                if doc.document.sign:
                    path_s = doc.document.sign.name
                    zip.write('media/' + path_s, arcname=path_s.split('/')[-1])
        zip.close()
    return zip_io.getvalue()
