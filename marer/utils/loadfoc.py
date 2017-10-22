import re

from marer import consts


def get_cell_percentage(cell_data):

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


def get_cell_bool(cell_data):

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


def get_cell_review_term_days(cell_data):

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


def get_cell_ensure_condition(cell_data):

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
            ensure_type = consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_PLEDGE
            ensure_value = int(ens_data.get('percentage'))
            return ensure_type, ensure_value

    for pattern in patterns_estate:
        matches = pattern.fullmatch(str(cell_data.value).lower())
        if matches:
            return consts.FO_PRODUCT_CONDITIONS_INSURANCE_TYPE_REAL_ESTATE, 100

    for pattern in patterns_none:
        matches = pattern.fullmatch(str(cell_data.value).lower())
        if matches:
            return None, 0


def get_cell_summ_range(cell_data):

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


def get_cell_value(sheet, col, row):
    sheet_idx = '{col}{row}'.format(col=str(col).upper(), row=row)
    return sheet[sheet_idx]
