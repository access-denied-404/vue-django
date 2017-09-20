from dateutil.relativedelta import relativedelta

from django.forms import Form, CharField, DecimalField, DateField, ChoiceField, BooleanField
from django.utils import timezone

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
    tender_gos_number = CharField(required=True)
    tender_placement_type = CharField(required=False)
    tender_exec_law = ChoiceField(required=False, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
    ])
    tender_publish_date = DateField(required=False)
    tender_start_cost = DecimalField(decimal_places=2, required=True)

    tender_responsible_full_name = CharField(required=False)
    tender_responsible_legal_address = CharField(required=False)
    tender_responsible_inn = CharField(required=False)
    tender_responsible_kpp = CharField(required=False)
    tender_responsible_ogrn = CharField(required=False)

    bg_sum = DecimalField(decimal_places=2, required=True)
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


class BankGuaranteeProduct(FinanceProduct):
    _humanized_name = 'Банковская гарантия'

    def get_documents_list(self):
        docs = []

        # here we getting a list with ends of year quarters
        curr_localized_datetime = timezone.localtime(timezone.now(), timezone.get_current_timezone())
        curr_date = curr_localized_datetime.date()

        prev_month_start_date = (curr_date - relativedelta(months=1)).replace(day=1)
        yr_quartals_start_months = [1, 4, 7, 10]
        curr_quartal_start_date = prev_month_start_date
        while curr_quartal_start_date.month not in yr_quartals_start_months:
            curr_quartal_start_date -= relativedelta(months=1)
        yr_quarters_cnt = 4  # first quarter will catch as finished quarter on start
        quarters_start_date = curr_quartal_start_date - relativedelta(months=yr_quarters_cnt*3)
        quarters_curr_date = quarters_start_date

        while quarters_curr_date <= curr_date:

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
