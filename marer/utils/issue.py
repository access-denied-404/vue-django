import math
from django.core.exceptions import ObjectDoesNotExist

from marer import consts
from marer.models import BankMinimalCommission
from marer.utils.datetime_utils import get_datetime_as_excel_number, get_date_diff_in_days


def issue_term_in_months(start_date, end_date):

    def _year(datetime):
        return datetime.year

    def _month(datetime):
        return datetime.month

    months = 1 + (_year(end_date) - _year(start_date)) * 12 + _month(end_date) - _month(start_date)
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
    AN10 = get_date_diff_in_days(bg_end_date, bg_start_date)

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


def sum2str(value):
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
        for id, group in enumerate(groups):
            i1, i2, i3 = list([int(g) for g in group])
            unit_id = len(groups) - id
            current_unit = unit[unit_id]
            gender = current_unit[3]
            digits.append(hundred[i1])
            if i2 > 1:
                if i3 != 0:
                    text = tens[i2] + ' ' + ten[gender][i3]
                else:
                    text = tens[i2] # 20-99
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
                else:
                    digits.append(morph(group, *current_unit[:3]))
        currency.append(str(kop) if int(kop) > 0 else zero)
        currency.append(morph(kop, *unit[0][:3]))
    return '(' + ' '.join(digits).strip() + ') ' + ' '.join(currency).strip()
