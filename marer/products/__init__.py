from django.forms import Form, CharField, DecimalField

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
    bg_sum = DecimalField(required=True)
    # term = None  # fixme define a field and determine it's meaning


class BankGuaranteeProduct(FinanceProduct):
    _humanized_name = 'Банковская гарантия'

    def get_documents_list(self):
        return [
            FinanceProductDocumentItem(
                code='company_charter',
                name='Устав'
            ),
            FinanceProductDocumentItem(
                code='accounting_balance_',
                name='Бухгалтерский баланс и отчет о фин. результатах',
                description='ББ и ОПиУ за отчетный период',
            ),
            FinanceProductDocumentItem(
                code='passport_copy_of_org_head',
                name='Копия паспорта руководителя организации',
            ),
            FinanceProductDocumentItem(
                code='manager_appointment_decision',
                name='Решение/протокол о назначении руководителя',
            ),
            FinanceProductDocumentItem(
                code='location_ownership_document',
                name='Договор аренды, субаренды, или свидетельство о праве собственности по месту нахождения',
            ),
            FinanceProductDocumentItem(
                code='org_financical_result_',
                name='УБ и отчет о фин. результатах за последний квартал',
            ),
        ]

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
