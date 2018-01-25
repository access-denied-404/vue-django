import json

import os

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import number_format
from django.utils.functional import cached_property
from django.utils.timezone import now

from marer import consts
from marer.models.base import Document, set_obj_update_time, BankMinimalCommission
from marer.models.finance_org import FinanceOrganization, FinanceOrgProductProposeDocument
from marer.models.issuer import Issuer, IssuerDocument
from marer.products import get_finance_products_as_choices, FinanceProduct, get_finance_products, BankGuaranteeProduct
from marer.utils import CustomJSONEncoder, kontur

__all__ = [
    'Issue', 'IssueDocument', 'IssueClarification',
    'IssueClarificationMessage', 'IssueFinanceOrgProposeClarificationMessageDocument'
]


class Issue(models.Model):
    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'
        ordering = ('-id',)

    product = models.CharField(verbose_name='банковский продукт', max_length=32, blank=False, null=False, choices=get_finance_products_as_choices())
    status = models.CharField(verbose_name='статус заявки', max_length=32, blank=False, null=False, choices=[
        (consts.ISSUE_STATUS_REGISTERING, 'Оформление заявки'),
        (consts.ISSUE_STATUS_REVIEW, 'Рассмотрение заявки'),
        (consts.ISSUE_STATUS_FINISHED, 'Завершена'),
        (consts.ISSUE_STATUS_CANCELLED, 'Отменена'),
    ], default=consts.ISSUE_STATUS_REGISTERING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='пользователь', on_delete=models.DO_NOTHING, null=False)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='менеджер по заявке',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='managed_issues'
    )
    comment = models.TextField(verbose_name='комментарий к заявке', blank=True, null=False, default='')
    private_comment = models.TextField(verbose_name='приватный комментарий к заявке', blank=True, null=False, default='')
    updated_at = models.DateTimeField(verbose_name='время обновления', auto_now=True, null=False)
    created_at = models.DateTimeField(verbose_name='время создания', auto_now_add=True, null=False)

    issuer = models.ForeignKey(Issuer, on_delete=models.SET_NULL, blank=True, null=True)
    issuer_inn = models.CharField(verbose_name='ИНН заявителя', max_length=32, blank=True, null=False, default='')
    issuer_kpp = models.CharField(verbose_name='КПП заявителя', max_length=32, blank=True, null=False, default='')
    issuer_ogrn = models.CharField(verbose_name='ОГРН заявителя', max_length=32, blank=True, null=False, default='')
    issuer_full_name = models.CharField(verbose_name='полное наименование заявителя', max_length=512, blank=True, null=False, default='')
    issuer_short_name = models.CharField(verbose_name='краткое наименование заявителя', max_length=512, blank=True, null=False, default='')

    issuer_foreign_name = models.CharField(verbose_name='наименование заявителя на иностранном', max_length=512, blank=True, null=False, default='')
    issuer_legal_address = models.CharField(verbose_name='юридическй адрес заявителя', max_length=512, blank=True, null=False, default='')
    issuer_fact_address = models.CharField(verbose_name='фактический адрес заявителя', max_length=512, blank=True, null=False, default='')
    issuer_okpo = models.CharField(verbose_name='код ОКПО заявителя', max_length=32, blank=True, null=False, default='')
    issuer_okato = models.CharField(verbose_name='код ОКАТО заявителя', max_length=32, blank=True, null=False, default='')
    issuer_registration_date = models.DateField(verbose_name='дата регистрации', blank=True, null=True)
    issuer_ifns_reg_date = models.DateField(verbose_name='дата постановки на учет в ИФНС', blank=True, null=True)
    issuer_ifns_reg_cert_number = models.CharField(verbose_name='номер свидетельства о постановке на учет ИФНС', max_length=32, blank=True, null=False, default='')
    issuer_okopf = models.CharField(verbose_name='код ОКОПФ (правовая форма) заявителя', max_length=32, blank=True, null=False, default='')
    issuer_okved = models.CharField(verbose_name='код ОКВЭД (основное направление деятельности) заявителя', max_length=32, blank=True, null=False, default='')

    issuer_head_first_name = models.CharField(verbose_name='имя руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_last_name = models.CharField(verbose_name='фамилия руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_middle_name = models.CharField(verbose_name='отчество руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_birthday = models.DateField(verbose_name='дата рождения руководителя', blank=True, null=True)
    issuer_head_org_position_and_permissions = models.CharField(verbose_name='должность, полномочия руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_phone = models.CharField(verbose_name='телефон руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_passport_series = models.CharField(verbose_name='серия паспорта руководителя', max_length=32, blank=True, null=False, default='')
    issuer_head_passport_number = models.CharField(verbose_name='номер паспорта руководителя', max_length=32, blank=True, null=False, default='')
    issuer_head_passport_issue_date = models.DateField(verbose_name='дата выдачи паспорта руководителя', blank=True, null=True)
    issuer_head_passport_issued_by = models.CharField(verbose_name='кем выдан паспорт руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_residence_address = models.CharField(verbose_name='адрес прописки руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_education_level = models.CharField(verbose_name='образование руководителя', max_length=512, blank=True, null=False, default='')
    issuer_head_org_work_experience = models.CharField(verbose_name='стаж работы руководителя в компании', max_length=512, blank=True, null=False, default='')
    issuer_head_share_in_authorized_capital = models.CharField(verbose_name='доля руководителя в уставном капиталле', max_length=512, blank=True, null=False, default='')
    issuer_head_industry_work_experience = models.CharField(verbose_name='опыт работы руководителя в отрасли', max_length=512, blank=True, null=False, default='')
    issuer_prev_org_info = models.CharField(verbose_name='предыдущее место работы руководителя, отрасль, должность', max_length=512, blank=True, null=False, default='')

    tender_gos_number = models.CharField(verbose_name='госномер или ссылка на тендер', max_length=512, blank=True, null=False, default='')
    tender_placement_type = models.CharField(verbose_name='способ определения поставщика в тендере', max_length=32, blank=True, null=False, default='')
    tender_exec_law = models.CharField(verbose_name='вид банковской гарантии', max_length=32, blank=True, null=True, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
        (consts.TENDER_EXEC_LAW_185_FZ, '185-ФЗ'),
        (consts.TENDER_EXEC_LAW_COMMERCIAL, 'Коммерческий'),
        (consts.TENDER_EXEC_LAW_CUSTOMS, 'Таможенная'),
        (consts.TENDER_EXEC_LAW_VAT, 'Возврат НДС'),
    ])
    tender_publish_date = models.DateField(verbose_name='дата публикации тендера', blank=True, null=True)
    tender_start_cost = models.DecimalField(verbose_name='начальная цена тендера', max_digits=12, decimal_places=2, blank=True, null=True)

    tender_contract_type = models.CharField(verbose_name='вид работ в тендере', max_length=32, blank=True, null=True, choices=[
        (consts.TENDER_CONTRACT_TYPE_SUPPLY_CONTRACT, 'Поставка товара'),
        (consts.TENDER_CONTRACT_TYPE_SERVICE_CONTRACT, 'Оказание услуг'),
        (consts.TENDER_CONTRACT_TYPE_WORKS_CONTRACT, 'Выполнение работ'),
    ])
    tender_has_prepayment = models.NullBooleanField(verbose_name='авансирование в тендере', blank=True, null=True)

    tender_responsible_full_name = models.CharField(verbose_name='полное наименование организатора тендера', max_length=512, blank=True, null=False, default='')
    tender_responsible_legal_address = models.CharField(verbose_name='юридический адрес организатора тендера', max_length=512, blank=True, null=False, default='')
    tender_responsible_inn = models.CharField(verbose_name='ИНН организатора тендера', max_length=32, blank=True, null=False, default='')
    tender_responsible_kpp = models.CharField(verbose_name='КПП организатора тендера', max_length=32, blank=True, null=False, default='')
    tender_responsible_ogrn = models.CharField(verbose_name='ОГРН организатора тендера', max_length=32, blank=True, null=False, default='')

    bg_commercial_contract_subject = models.CharField(verbose_name='предмет договора', max_length=512, blank=True, null=False, default='')
    bg_commercial_contract_place_of_work = models.CharField(verbose_name='место выполнения работ', max_length=512, blank=True, null=False, default='')
    bg_commercial_contract_sum = models.DecimalField(verbose_name='сумма контракта', max_digits=12, decimal_places=2, blank=True, null=True)
    bg_commercial_contract_sign_date = models.DateField(verbose_name='дата заключения договора', blank=True, null=True)
    bg_commercial_contract_end_date = models.DateField(verbose_name='дата завершения договора', blank=True, null=True)

    bg_sum = models.DecimalField(verbose_name='сумма', max_digits=12, decimal_places=2, blank=True, null=True)
    bg_currency = models.CharField(verbose_name='валюта', max_length=32, blank=True, null=True, choices=[
        (consts.CURRENCY_RUR, 'Рубль'),
        (consts.CURRENCY_USD, 'Доллар'),
        (consts.CURRENCY_EUR, 'Евро'),
    ])
    bg_start_date = models.DateField(verbose_name='дата начала действия банковской гарантии', blank=True, null=True)
    bg_end_date = models.DateField(verbose_name='дата завершения действия банковской гарантии', blank=True, null=True)
    bg_deadline_date = models.DateField(verbose_name='крайний срок выдачи банковской гарантии', blank=True, null=True)
    bg_type = models.CharField(verbose_name='тип банковской гарантии', max_length=32, blank=True, null=True, choices=[
        (consts.BG_TYPE_APPLICATION_ENSURE, 'Обеспечение заявки'),
        (consts.BG_TYPE_CONTRACT_EXECUTION, 'Исполнение контракта'),
        (consts.BG_TYPE_REFUND_OF_ADVANCE, 'Возврат аванса'),
        (consts.BG_TYPE_WARRANTY_ENSURE, 'Обеспечение гарантийных обязательств'),
    ])

    credit_product_is_credit = models.NullBooleanField(verbose_name='кредит', blank=True, null=True)
    credit_product_is_credit_line = models.NullBooleanField(verbose_name='кредитная линия', blank=True, null=True)
    credit_product_is_overdraft = models.NullBooleanField(verbose_name='овердрафт', blank=True, null=True)
    credit_product_interest_rate = models.FloatField(verbose_name='ставка (в % годовых)', blank=True, null=True)
    credit_repayment_schedule = models.CharField(verbose_name='график погашения', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_CREDIT_REPAYMENT_SCHEDULE_EQUAL_SHARES, 'Равными долями'),
        (consts.ISSUE_CREDIT_REPAYMENT_SCHEDULE_END_OF_TERM, 'В конце срока'),
    ])
    credit_product_term = models.CharField(verbose_name='срок продукта', max_length=512, blank=True, null=False, default='')
    credit_product_cl_tranche_term = models.CharField(verbose_name='срок транша (в случае кредитной линии)', max_length=512, blank=True, null=False, default='')
    credit_purpose_type = models.CharField(verbose_name='цель кредита', max_length=32, blank=True, null=True, choices=[
        (consts.CREDIT_PURPOSE_TYPE_WORK_CAPITAL_REFILL, 'Пополнение оборотных средств'),
        (consts.CREDIT_PURPOSE_TYPE_CONTRACT_EXEC, 'Исполнение контракта'),
    ])
    credit_purpose = models.CharField(verbose_name='цель кредита (подробно)', max_length=512, blank=True, null=False, default='')
    credit_repayment_sources = models.CharField(verbose_name='источники погашения', max_length=512, blank=True, null=False, default='')

    factoring_product_is_regressive = models.NullBooleanField(verbose_name='регрессивный факторинг', blank=True, null=True)
    factoring_product_is_not_regressive = models.NullBooleanField(verbose_name='факторинг без регресса', blank=True, null=True)
    factoring_product_is_cred_risks_cover = models.NullBooleanField(verbose_name='покрытие кредитных рисков', blank=True, null=True)
    factoring_product_is_suppliers_financing = models.NullBooleanField(verbose_name='финансирование поставщиков', blank=True, null=True)
    factoring_product_is_orders_financing = models.NullBooleanField(verbose_name='финансирование заказов', blank=True, null=True)
    factoring_product_is_closed = models.NullBooleanField(verbose_name='закрытый факторинг', blank=True, null=True)
    factoring_product_is_export = models.NullBooleanField(verbose_name='экспортный факторинг', blank=True, null=True)
    factoring_product_is_import = models.NullBooleanField(verbose_name='импортный факторинг', blank=True, null=True)
    factoring_avg_actual_buyers_payment_term = models.IntegerField(verbose_name='Средний фактический срок оплаты покупателями (дней)', blank=True, null=True)
    factoring_max_contract_deferred_payment_term = models.IntegerField(verbose_name='Максимальный период отсрочки платежа по контрактам (дней)', blank=True, null=True)
    factoring_sale_goods_or_services = models.CharField(verbose_name='виды реализуемых товаров/услуг', max_length=512, blank=True, null=False, default='')
    factoring_manufactured_goods = models.CharField(verbose_name='виды производимых товаров', max_length=512, blank=True, null=False, default='')

    leasing_term = models.IntegerField(verbose_name='Срок лизинга (мес.)', blank=True, null=True)
    leasing_advance_payment_rate = models.FloatField(verbose_name='Авансовый платеж (%)', blank=True, null=True)
    leasing_payment_schedule = models.CharField(verbose_name='График платежей', max_length=512, blank=True, null=False, default='')
    leasing_asset_operation_territory = models.CharField(verbose_name='Территория эксплуатации предмета лизинга', max_length=512, blank=True, null=False, default='')
    leasing_bank_account_number = models.CharField(verbose_name='Рассчетный счет заявителя', max_length=32, blank=True, null=False, default='')
    leasing_corr_account_number = models.CharField(verbose_name='Корреспондентский счет', max_length=32, blank=True, null=False, default='')
    leasing_bank_name = models.CharField(verbose_name='Банк', max_length=512, blank=True, null=False, default='')
    leasing_bank_identification_code = models.CharField(verbose_name='БИК', max_length=32, blank=True, null=False, default='')
    leasing_holder_on_balance_name = models.CharField(verbose_name='Балансодержатель', max_length=512, blank=True, null=False, default='')
    leasing_holder_on_balance_ogrn = models.CharField(verbose_name='ОГРН балансодержателя', max_length=32, blank=True, null=False, default='')
    leasing_holder_on_balance_inn = models.CharField(verbose_name='ИНН балансодержателя', max_length=32, blank=True, null=False, default='')
    leasing_holder_on_balance_kpp = models.CharField(verbose_name='КПП балансодержателя', max_length=32, blank=True, null=False, default='')
    leasing_insurer_name = models.CharField(verbose_name='Страхователь', max_length=512, blank=True, null=False, default='')
    leasing_insurer_ogrn = models.CharField(verbose_name='ОГРН страхователя', max_length=32, blank=True, null=False, default='')
    leasing_insurer_inn = models.CharField(verbose_name='ИНН страхователя', max_length=32, blank=True, null=False, default='')
    leasing_insurer_kpp = models.CharField(verbose_name='КПП страхователя', max_length=32, blank=True, null=False, default='')

    curr_year_sales_value = models.DecimalField(verbose_name='Объем продаж за текущий год, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)
    prev_year_sales_value = models.DecimalField(verbose_name='Объем продаж за прошлый год, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)
    curr_year_sales_value_inc_deferment = models.DecimalField(verbose_name='Объем продаж за текущий год, в том числе на условиях отсрочки, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)
    prev_year_sales_value_inc_deferment = models.DecimalField(verbose_name='Объем продаж за прошлый год, в том числе на условиях отсрочки, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)
    curr_year_expected_sales_value = models.DecimalField(verbose_name='Ожидаемые продажи за текущий год по экспорту, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)
    prev_year_expected_sales_value = models.DecimalField(verbose_name='Ожидаемые продажи за прошлый год по экспорту, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)
    curr_year_expected_sales_value_inc_deferment = models.DecimalField(verbose_name='Ожидаемые продажи за текущий год по экспорту в том числе с отсрочкой платежа, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)
    prev_year_expected_sales_value_inc_deferment = models.DecimalField(verbose_name='Ожидаемые продажи за прошлый год по экспорту в том числе с отсрочкой платежа, млн. рублей без НДС', max_digits=12, decimal_places=2, blank=True, null=True)

    formalize_note = models.TextField(verbose_name='подпись к документам для оформления', blank=True, null=False, default='')
    final_note = models.TextField(verbose_name='подпись к итоговым документам', blank=True, null=False, default='')

    balance_code_1300_offset_0 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_code_1600_offset_0 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_code_2110_offset_0 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_code_2400_offset_0 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    balance_code_1300_offset_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_code_1600_offset_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_code_2110_offset_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_code_2400_offset_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    avg_employees_cnt_for_prev_year = models.IntegerField(verbose_name='Средняя численность работников за предшествующий календарный год', blank=False, null=False, default=1)
    issuer_web_site = models.CharField(verbose_name='Web-сайт', max_length=512, blank=True, null=False, default='')
    issuer_accountant_org_or_person = models.CharField(verbose_name='ФИО гл.бухгалтера / наименование организации, осуществляющей ведение бух.учёта', max_length=512, blank=True, null=False, default='')
    issuer_post_address = models.CharField(verbose_name='почтовый адрес заявителя (с индексом) в т.ч. для отправки банковской гарантии', max_length=512, blank=True, null=False, default='')
    bg_is_benefeciary_form = models.NullBooleanField(verbose_name='БГ по форме Бенефециара', blank=True, null=True)
    is_indisputable_charge_off = models.NullBooleanField(verbose_name='право на бесспорное списание', blank=True, null=True)
    tender_contract_subject = models.CharField(verbose_name='предмет контракта', max_length=512, blank=True, null=False, default='')
    issuer_has_overdue_debts_for_last_180_days = models.NullBooleanField(verbose_name='Наличие просроченной задолженности по всем кредитам за последние 180 дней', blank=True, null=True)
    issuer_overdue_debts_info = models.TextField(verbose_name='Причины и обстоятельства просрочек', blank=True, null=False, default='')

    deal_has_beneficiary = models.NullBooleanField(verbose_name='наличие бенефициара по сделке', blank=True, null=True)
    issuer_bank_relations_term = models.CharField(verbose_name='срок отношений с Банком', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_DEAL_BANK_RELATIONS_TERM_SHORT, 'Краткосрочные'),
        (consts.ISSUE_DEAL_BANK_RELATIONS_TERM_LONG, 'Долгосрочные'),
    ])
    issuer_activity_objective = models.CharField(verbose_name='цели финансово-хозяйственной детяельности', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_ISSUER_ACTIVITY_OBJECTIVE_PROFIT_MAKING, 'Получение прибыли'),
        (consts.ISSUE_ISSUER_ACTIVITY_OBJECTIVE_OTHER, 'Иное'),
    ])
    issuer_finance_situation = models.CharField(verbose_name='финансовое положение', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_ISSUER_FINANCE_SITUATION_SATISFIED, 'Удовлетворительное'),
        (consts.ISSUE_ISSUER_FINANCE_SITUATION_UNSATISFIED, 'Неудовлетворительное'),
    ])
    issuer_business_reputation = models.CharField(verbose_name='деловая репутация', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_ISSUER_BUSINESS_REPUTATION_POSITIVE, 'Положительная'),
        (consts.ISSUE_ISSUER_BUSINESS_REPUTATION_NOT_PRESENT, 'Отсутствует'),
    ])
    issuer_funds_source = models.CharField(verbose_name='источник происхождения денежных средств', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUER_FUNDS_SOURCE_LOAN_FUNDS, 'Заемные средства'),
        (consts.ISSUER_FUNDS_SOURCE_OTHER, 'Иное'),
    ])

    issuer_org_management_collegial_executive_name = models.CharField(verbose_name='Коллегиальный исполнительный орган: наименование', max_length=512, blank=True, null=False, default='')
    issuer_org_management_collegial_executive_fio = models.CharField(verbose_name='Коллегиальный исполнительный орган: ФИО', max_length=512, blank=True, null=False, default='')
    issuer_org_management_directors_or_supervisory_board_name = models.CharField(verbose_name='Совет директоров (наблюдательный совет): наименование', max_length=512, blank=True, null=False, default='')
    issuer_org_management_directors_or_supervisory_board_fio = models.CharField(verbose_name='Совет директоров (наблюдательный совет): ФИО', max_length=512, blank=True, null=False, default='')
    issuer_org_management_other_name = models.CharField(verbose_name='Иной орган управления организации заявителя: наименование', max_length=512, blank=True, null=False, default='')
    issuer_org_management_other_fio = models.CharField(verbose_name='Иной орган управления организации заявителя: ФИО', max_length=512, blank=True, null=False, default='')

    application_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='application_docs_links'
    )
    doc_ops_mgmt_conclusion_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doc_ops_mgmt_conclusion_docs_links'
    )

    sec_dep_conclusion_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sec_dep_conclusion_docs_links'
    )

    @cached_property
    def passed_prescoring(self):
        return self.bank_commission and self.check_stop_factors_validity

    @cached_property
    def bank_commission(self):

        Q25 = 0.0027  # Процент: 0,27% (процент чего?)
        M10 = 0.1  # Предоставление гарантии по форме заказчика: 10%
        M11 = 0.1  # Контрактом предусмотрена возможность выплаты Аванса: 10%
        M12 = 0.05  # Гарантия в рамках 185-ФЗ: 5%
        M13 = 0.1  # Гарантия качества: 10%
        M14 = 0.15  # Подтверждение опыта исполнения контрактов (более 5 документов): 15%
        M15 = 0.05  # Увеличение/продление срока контракта: 5%

        E7 = self.bg_start_date
        F10 = self.bg_sum
        F11 = self.bg_end_date
        F17 = self.bg_is_benefeciary_form
        F18 = self.tender_has_prepayment
        F19 = self.tender_exec_law == consts.TENDER_EXEC_LAW_185_FZ  # Гарантия в рамках 185-ФЗ: +/-
        F20 = self.bg_type == consts.BG_TYPE_WARRANTY_ENSURE  # Гарантия качества: +/-
        F21 = False  # Подтверждение опыта исполнения контрактов (более 5 документов): +/-
        F22 = False  # Увеличение/продление срока контракта: +/-

        # F23: **Пусто**
        # M16: **Пусто**
        # M130: **Пусто**

        def _year(datetime):
            return datetime.year

        def _month(datetime):
            return datetime.month

        O25 = 1 + (_year(F11) - _year(E7)) * 12 + _month(F11) - _month(E7)
        Q17 = float(F10) * O25 * Q25
        Q22 = Q17 * (
            1
            + (M10 if F17 else 0)
            + (M11 if F18 else 0)
            + (M12 if F19 else 0)
            + (M13 if F20 else 0)
            + (M15 if F21 else 0)
            + (M14 if F22 else 0)
            # + (M13 if F20 else 0)
            # + (M16 if F23 else 0)
        )
        try:
            min_com = BankMinimalCommission.objects.get(
                sum_min__lte=self.bg_sum,
                sum_max__gte=self.bg_sum,
                term_months_min__lte=O25,
                term_months_max__gte=O25,
            )
            O24 = min_com.commission
        except ObjectDoesNotExist:
            return None

        Q20 = O24 if Q22 < O24 else Q22  # Q20: =ЕСЛИ(Q22<O24;O24;Q22)
        return round(Q20, 2)

    @property
    def humanized_id(self):
        if self.id:
            return str(self.id).zfill(10)
        else:
            return 'БЕЗ НОМЕРА'

    @property
    def humanized_sum(self):
        if self.bg_sum:
            fmt_sum = number_format(self.bg_sum)
            if self.bg_currency == consts.CURRENCY_RUR:
                str_fmt = '{cost} руб.'
            elif self.bg_currency == consts.CURRENCY_USD:
                str_fmt = '${cost}'
            elif self.bg_currency == consts.CURRENCY_EUR:
                str_fmt = '€{cost}'
            else:
                str_fmt = '{cost}'
            return str_fmt.format(cost=fmt_sum)
        else:
            return '—'

    @property
    def sum_not_null(self):
        if self.bg_sum is None:
            return 0
        elif self.bg_sum.is_nan():
            return 0
        else:
            return self.bg_sum

    @property
    def humanized_status(self):
        return self.get_status_display() or ''

    @property
    def humanized_issuer_registration_date(self):
        return self.issuer_registration_date.strftime('%d.%m.%Y') if self.issuer_registration_date else ''

    @property
    def humanized_bg_end_date(self):
        return self.bg_end_date.strftime('%d.%m.%Y') if self.bg_end_date else ''
    
    @property
    def humanized_bg_type(self):
        return self.get_bg_type_display() or ''

    @property
    def humanized_bg_is_benefeciary_form(self):
        return 'Да' if self.bg_is_benefeciary_form else 'Нет'

    @property
    def humanized_is_indisputable_charge_off(self):
        return 'Да' if self.is_indisputable_charge_off else 'Нет'

    @property
    def humanized_issuer_has_overdue_debts_for_last_180_days(self):
        return 'Да' if self.issuer_has_overdue_debts_for_last_180_days else 'Нет'

    @property
    def humanized_tender_has_prepayment(self):
        return 'Да' if self.tender_has_prepayment else 'Нет'

    @property
    def humanized_tender_exec_law(self):
        return self.get_tender_exec_law_display() or ''

    @property
    def humanized_issuer_funds_source(self):
        return self.get_issuer_funds_source_display() or ''

    @property
    def humanized_issuer_business_reputation(self):
        return self.get_issuer_business_reputation_display() or ''

    @property
    def humanized_issuer_activity_objective(self):
        return self.get_issuer_activity_objective_display() or ''

    @property
    def humanized_deal_has_beneficiary(self):
        return 'Присутствует' if self.deal_has_beneficiary else 'Отсутствует'

    @property
    def humanized_issuer_finance_siuation(self):
        return self.get_issuer_finance_situation_display() or ''

    @property
    def humanized_issuer_bank_relations_term(self):
        return self.get_issuer_bank_relations_term_display() or ''

    @cached_property
    def beneficiaries_owner(self):
        return list(self.org_beneficiary_owners.order_by('id').all())

    @cached_property
    def bank_accounts(self):
        return list(self.org_bank_accounts.order_by('id').all())

    @cached_property
    def founders_with_25_share(self):
        data = list(self.issuer_founders_legal.all().values('name', 'auth_capital_percentage'))
        physical = list(self.issuer_founders_physical.all().values('fio', 'auth_capital_percentage'))
        # добираем данные с переименовкой поля для одинакового вывода
        data += [{
            'name': f['fio'],
            'auth_capital_percentage': f['auth_capital_percentage']
        } for f in physical]
        return data

    @cached_property
    def licences_as_string(self):
        return '\n'.join(['%s от %s' % (l.number, l.date_from.strftime('%d.%m.%Y')) for l in self.issuer_licences.all() if l.is_active()])

    def application_doc_admin_field(self):
        field_parts = []
        if self.application_doc:
            if self.application_doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(self.application_doc.file.url))
            if self.application_doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(self.application_doc.sign.url))
        if len(field_parts) > 0:
            return ', '.join(field_parts)
        else:
            return 'отсутствует'
    application_doc_admin_field.short_description = 'файл заявки'
    application_doc_admin_field.allow_tags = True

    def doc_ops_mgmt_conclusion_doc_admin_field(self):
        field_parts = []
        if not self.doc_ops_mgmt_conclusion_doc:
            url = reverse('admin:marer_issue_generate_doc_ops_mgmt_conclusion_doc', args=(self.id,))
            field_parts.append('<b><a href="{}">сформировать</a></b>'.format(url))
        else:
            if self.doc_ops_mgmt_conclusion_doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(self.doc_ops_mgmt_conclusion_doc.file.url))
            if self.doc_ops_mgmt_conclusion_doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(self.doc_ops_mgmt_conclusion_doc.sign.url))
        if len(field_parts) > 0:
            return ', '.join(field_parts)
        else:
            return 'отсутствует'
    doc_ops_mgmt_conclusion_doc_admin_field.short_description = 'файл заключения УРДО'
    doc_ops_mgmt_conclusion_doc_admin_field.allow_tags = True

    def sec_dep_conclusion_doc_admin_field(self):
        field_parts = []
        if not self.sec_dep_conclusion_doc:
            url = reverse('admin:marer_issue_generate_sec_dep_conclusion_doc', args=(self.id,))
            field_parts.append('<b><a href="{}">сформировать</a></b>'.format(url))
        else:
            if self.sec_dep_conclusion_doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(self.sec_dep_conclusion_doc.file.url))
            if self.sec_dep_conclusion_doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(self.sec_dep_conclusion_doc.sign.url))
        if len(field_parts) > 0:
            return ', '.join(field_parts)
        else:
            return 'отсутствует'
    sec_dep_conclusion_doc_admin_field.short_description = 'файл заключения ДБ'
    sec_dep_conclusion_doc_admin_field.allow_tags = True

    @property
    def issuer_head_passport_info(self):
        info_arr = []
        if self.issuer_head_passport_series and self.issuer_head_passport_number:
            info_arr.append('Паспорт серии {} №{}'.format(
                self.issuer_head_passport_series, self.issuer_head_passport_number))
            if self.issuer_head_passport_issued_by and self.issuer_head_passport_issue_date:
                info_arr.append('выдан {}, {}'.format(
                    self.issuer_head_passport_issued_by, self.issuer_head_passport_issue_date.strftime('%d.%m.%Y')))
        return ', '.join(info_arr)

    @property
    def max_state_available(self):
        # fixme implement issue validation for each status
        return consts.ISSUE_STATUS_REGISTERING

    def fill_from_issuer(self):
        self.issuer_inn = self.issuer.inn
        self.issuer_kpp = self.issuer.kpp
        self.issuer_ogrn = self.issuer.ogrn
        self.issuer_full_name = self.issuer.full_name
        self.issuer_short_name = self.issuer.short_name

    def get_product(self) -> FinanceProduct:
        for fp in get_finance_products():
            if fp.name == self.product:
                fp.set_issue(self)
                return fp
        raise ValueError('No finance products matched')

    def get_issuer_name(self):
        if self.issuer_short_name != '':
            return self.issuer_short_name
        elif self.issuer_full_name != '':
            return self.issuer_full_name
        else:
            return '—'

    def update_common_issue_doc(self, code, file):
        """
        Saves a document, adds coded document
        record to issue and it's issuer if exist.

        :param code: document identification code
        :param file: file object for saving
        """
        doc_file = Document()
        doc_file.file = file
        doc_file.save()

        code_issue_docs = self.common_documents.filter(code=code)
        for ci_doc in code_issue_docs:
            ci_doc.delete()

        issue_doc = IssueDocument()
        issue_doc.code = code
        issue_doc.document = doc_file
        issue_doc.issue = self
        issue_doc.save()

        if self.issuer is not None:
            code_issuer_docs_qs = self.issuer.issuer_documents.filter(code=code)
            if not code_issuer_docs_qs.exists():
                issuer_doc = IssuerDocument()
                issuer_doc.code = code
                issuer_doc.document = doc_file
                issuer_doc.issuer = self.issuer
                issuer_doc.save()

    def serialize_registering_data(self):
        reg_form_class = self.get_product().get_registering_form_class()
        reg_form = reg_form_class(self.__dict__)
        reg_form.full_clean()
        if not self.passed_prescoring and not reg_form.errors:
            reg_form.add_error('stop_factors', 'Не в рамках продукта')
        json_data = json.dumps(dict(
            formdata=reg_form.cleaned_data,
            errors=reg_form.errors,
        ), cls=CustomJSONEncoder)
        return json_data

    @cached_property
    def available_dashboard_views_names(self):
        available_views = ['issue_registering']

        reg_form_class = self.get_product().get_registering_form_class()
        reg_form = reg_form_class(self.__dict__)
        if reg_form.is_valid():
            available_views.append('issue_survey')
            available_views.append('issue_scoring')
        else:
            return available_views

        if not self.status == consts.ISSUE_STATUS_REGISTERING:
            available_views.append('issue_additional_documents_requests')

        if self.status in [consts.ISSUE_STATUS_FINISHED, consts.ISSUE_STATUS_CANCELLED]:
            available_views.append('issue_finished')

        return available_views

    def editable_dashboard_views(self):
        registering_views = [
            'issue_registering',
            'issue_common_documents_request',
            'issue_survey',
            'issue_scoring',
        ]
        review_views = [
            'issue_additional_documents_requests',
            'issue_finished',
        ]

        if self.status == consts.ISSUE_STATUS_REGISTERING:
            return registering_views
        if self.status == consts.ISSUE_STATUS_REVIEW:
            return review_views
        if self.status in [consts.ISSUE_STATUS_FINISHED, consts.ISSUE_STATUS_CANCELLED]:
            return []
        else:
            return ['issue_registering']

    def __str__(self):
        if self.bg_sum:
            str_repr = 'Заявка №{num} на {cost}, {product} для {issuer}'
        else:
            str_repr = 'Заявка №{num}, {product} для {issuer}'
        return str_repr.format(
            num=self.id,
            cost=self.humanized_sum,
            product=self.get_product().humanized_name,
            issuer=self.get_issuer_name(),
        )

    @property
    def propose_documents_ordered(self):
        return self.propose_documents.order_by('document_id')  # need null to be first

    @property
    def propose_documents_for_remote_sign(self):
        docs = []
        if self.application_doc and self.application_doc.file and self.application_doc.sign_state != consts.DOCUMENT_SIGN_VERIFIED:
            app_doc = IssueProposeDocument()
            app_doc.name = 'Заявление на предоставление банковской гарантии'
            app_doc.document = self.application_doc
            docs.append(app_doc)
        pdocs = self.propose_documents.filter(
            is_approved_by_manager=True
        ).exclude(
            document__sign_state=consts.DOCUMENT_SIGN_VERIFIED
        ).order_by('name')
        docs.extend(pdocs)
        return docs

    def fill_application_doc(self, commit=True):
        template_path = os.path.join(
            settings.BASE_DIR,
            'marer',
            'templates',
            'documents',
            'issue_application_doc.docx',
        )

        from marer.utils.documents import fill_docx_file_with_issue_data
        application_doc_file = fill_docx_file_with_issue_data(template_path, self)
        application_doc_file.name = 'application.docx'

        app_doc = Document()
        app_doc.file = application_doc_file
        app_doc.save()
        self.application_doc = app_doc
        if commit:
            self.save()
        application_doc_file.close()

    def fill_doc_ops_mgmt_conclusion(self, commit=True):

        ve = ValidationError(None)
        ve.error_list = []
        issuer_reg_delta = relativedelta(
            timezone.localdate(timezone.now(), timezone.get_current_timezone()),
            self.issuer_registration_date,
        )
        if issuer_reg_delta.years <= 0 and issuer_reg_delta.months <= 6:
            ve.error_list.append('Обнаружен стоп-фактор: организация зарегистрирована менее 6 месецев назад')

        if self.sec_dep_conclusion_doc is None or self.sec_dep_conclusion_doc.file is None:
            ve.error_list.append('Отсутствует заключение ДБ')

        if len(ve.error_list) > 0:
            raise ve

        template_path = os.path.join(
            settings.BASE_DIR,
            'marer',
            'templates',
            'documents',
            'issue_doc_ops_mgmt_conclusion.docx'
        )

        from marer.utils.documents import fill_docx_file_with_issue_data
        doc_ops_mgmt_conclusion_file = fill_docx_file_with_issue_data(template_path, self)
        doc_ops_mgmt_conclusion_file.name = 'doc_ops_mgmt_conclusion.docx'
        domc_doc = Document()
        domc_doc.file = doc_ops_mgmt_conclusion_file
        domc_doc.save()
        self.doc_ops_mgmt_conclusion_doc = domc_doc
        if commit:
            self.save()
        doc_ops_mgmt_conclusion_file.close()

    def fill_sec_dep_conclusion_doc(self, commit=True):

        ve = ValidationError(None)
        ve.error_list = []
        issuer_reg_delta = relativedelta(
            timezone.localdate(timezone.now(), timezone.get_current_timezone()),
            self.issuer_registration_date,
        )
        if issuer_reg_delta.years <= 0 and issuer_reg_delta.months <= 6:
            ve.error_list.append('Обнаружен стоп-фактор: организация зарегистрирована менее 6 месецев назад')

        if len(ve.error_list) > 0:
            raise ve

        template_path = os.path.join(
            settings.BASE_DIR,
            'marer',
            'templates',
            'documents',
            'issue_sec_dep_conclusion.docx'
        )

        from marer.utils.documents import fill_docx_file_with_issue_data
        sec_dep_conclusion_file = fill_docx_file_with_issue_data(template_path, self)
        sec_dep_conclusion_file.name = 'sec_dep_conclusion.docx'
        new_doc = Document()
        new_doc.file = sec_dep_conclusion_file
        new_doc.save()
        self.sec_dep_conclusion_doc = new_doc
        if commit:
            self.save()
        sec_dep_conclusion_file.close()

    def validate_stop_factors(self):
        ve = ValidationError(None)
        ve.error_list = []

        try:
            kontur_benefitiar_analytics_data = kontur.analytics(inn=self.tender_responsible_inn, ogrn=self.tender_responsible_ogrn)
            kontur_principal_analytics_data = kontur.analytics(inn=self.issuer_inn, ogrn=self.issuer_ogrn)

            # principal stop factors
            if kontur_principal_analytics_data.get('m4001', False):
                ve.error_list.append(
                    'Исполнитель найден в реестре недобросоветных поставщиков. '
                    'Рассмотрение заявки невозможно до устранения стоп-фактора.'
                )
            if kontur_principal_analytics_data.get('m7003', False):
                ve.error_list.append('Обнаружен стоп-фактор: организация зарегистрирована менее 6 месецев назад')
            if kontur_principal_analytics_data.get('m5004', False):
                ve.error_list.append(
                    'Организация была найдена в списке юридических лиц, имеющих задолженность по уплате налогов.')
            for bl_inn_start in ['09', '01', '05', '06', '07', '15', '17', '20', '91', '92', '2632']:
                if self.issuer_inn.startswith(bl_inn_start):
                    ve.error_list.append('Обнаружен стоп-фактор: исполнитель находится в необслуживаемом регионе')
                    break

            # benefitiar stop factors
            if self.tender_exec_law in [consts.TENDER_EXEC_LAW_44_FZ, consts.TENDER_EXEC_LAW_223_FZ]:
                if kontur_benefitiar_analytics_data.get('q4005', 0) > 0:
                    ve.error_list.append('Бенефициар не найден в реестре государственных заказчиков')
            for bl_inn_start in ['91', '92']:
                if self.tender_responsible_inn.startswith(bl_inn_start):
                    ve.error_list.append('Обнаружен стоп-фактор: заказчик находится в необслуживаемом регионе')
                    break

        except Exception:
            ve.error_list.append('Не удалось проверить заявку на стоп-факторы')

        if len(ve.error_list) > 0:
            raise ve

    @cached_property
    def check_stop_factors_validity(self):
        try:
            self.validate_stop_factors()
        except ValidationError:
            return False
        else:
            return True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.bg_start_date:
            self.bg_start_date = timezone.now()
        if not self.product or self.product == '':
            self.product = BankGuaranteeProduct().name
        super().save(force_insert, force_update, using, update_fields)

        pdocs = FinanceOrgProductProposeDocument.objects.all()
        if self.status == consts.ISSUE_STATUS_REVIEW \
                and not self.propose_documents.exists() \
                and pdocs.exists():
            for pdoc in pdocs:
                new_doc = IssueProposeDocument()
                new_doc.issue = self
                new_doc.name = pdoc.name
                new_doc.code = pdoc.code
                if pdoc.sample:
                    new_doc.sample = pdoc.sample
                new_doc.save()


class IssueDocument(models.Model):
    class Meta:
        verbose_name = 'общий документ'
        verbose_name_plural = 'общие документы'

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='common_documents'
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='common_issue_links'
    )
    code = models.CharField(
        max_length=512,
        null=True,
        blank=True,
    )


class IssueProposeDocument(models.Model):
    class Meta:
        verbose_name = 'документ для банка'
        verbose_name_plural = 'документы для банка'

    issue = models.ForeignKey(
        Issue,
        verbose_name='предложение заявки в банк',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='propose_documents'
    )
    name = models.CharField(max_length=512, blank=False, null=False, default='')
    sample = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='propose_samples_links'
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='propose_links'
    )
    code = models.CharField(
        choices=[
            (consts.FO_PRODUCT_PROPOSE_DOC_HEAD_PASSPORT, 'Паспорт генерального директора (руководителя)'),
            (consts.FO_PRODUCT_PROPOSE_DOC_HEAD_STATUTE, 'Устав организации'),
        ],
        max_length=512,
        null=True,
        blank=True,
    )
    is_approved_by_manager = models.NullBooleanField('проверка менеджером', choices=[
        (None, 'Не проверен'),
        (True, 'Подтвержден'),
        (False, 'Забракован'),
    ], null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, chain_docs_update=False):
        # todo does it has any sense?
        # if not chain_docs_update and self.propose and self.propose.issue_id and self.document and self.document.file and self.code is not None and self.code != '':
        #     other_proposes = self.propose.issue.proposes.all()
        #     if self.id:
        #         other_proposes = other_proposes.exclude(id=self.id)
        #     for propose in other_proposes:
        #         opdocs = propose.propose_documents.filter(code=self.code)
        #         for opdoc in opdocs:
        #             opdoc.document = self.document
        #             opdoc.save(chain_docs_update=True)

        super().save(force_insert, force_update, using, update_fields)


class IssueClarification(models.Model):
    class Meta:
        verbose_name = 'дозапрос'
        verbose_name_plural = 'дозапросы'

    issue = models.ForeignKey(
        Issue,
        verbose_name='заявка',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='clarifications'
    )
    initiator = models.CharField(verbose_name='инициатор', max_length=32, blank=False, null=False, choices=[
        (consts.IFOPC_INITIATOR_FINANCE_ORG, 'Финансовая организация'),
        (consts.IFOPC_INITIATOR_ISSUER, 'Заявитель'),
    ])
    updated_at = models.DateTimeField(verbose_name='время обновления', auto_now=True, null=False)
    created_at = models.DateTimeField(verbose_name='время создания', auto_now_add=True, null=False)

    def __str__(self):
        str_args = (
            self.id,
            self.issue.id,
            self.created_at.strftime('%d.%m.%Y')
        )
        return 'Дозапрос №{} по заявке №{} от {}'.format(*str_args)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        set_obj_update_time(self.issue)
        return super().save(force_insert, force_update, using, update_fields)


class IssueClarificationMessage(models.Model):
    class Meta:
        verbose_name = 'сообщение по дозапросу'
        verbose_name_plural = 'сообщения по дозапросу'

    clarification = models.ForeignKey(
        IssueClarification,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='clarification_messages'
    )
    message = models.TextField(verbose_name='сообщение', blank=False, null=False, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='пользователь', on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField(verbose_name='время создания', auto_now_add=True, null=False)

    def __str__(self):
        return 'Сообщение по дозапросу №{num} от пользователя {user} в {created}'.format(
            num=self.clarification_id,
            user=self.user,
            created=self.created_at,
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        set_obj_update_time(self.clarification)
        return super().save(force_insert, force_update, using, update_fields)


class IssueFinanceOrgProposeClarificationMessageDocument(models.Model):
    clarification_message = models.ForeignKey(
        IssueClarificationMessage,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='documents_links'
    )
    name = models.CharField(max_length=512, blank=False, null=False, default='')
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clarification_messages_links'
    )


class IssueBGProdAffiliate(models.Model):
    class Meta:
        verbose_name = 'аффилированная компания'
        verbose_name_plural = 'аффилированные компании'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_affiliates')
    name = models.CharField(verbose_name='наименование', max_length=512, blank=False, null=False, default='')
    legal_address = models.CharField(verbose_name='юридический адрес', max_length=512, blank=True, null=False, default='')
    inn = models.CharField(verbose_name='ИНН', max_length=512, blank=True, null=False, default='')
    activity_type = models.CharField(verbose_name='вид деятельности', max_length=512, blank=True, null=False, default='')
    aff_percentage = models.CharField(verbose_name='доля участия', max_length=512, blank=True, null=False, default='')
    aff_type = models.CharField(verbose_name='отношение к организации', max_length=512, blank=True, null=False, default='')


class IssueLeasingProdAsset(models.Model):
    class Meta:
        verbose_name = 'лизинговое имущество'
        verbose_name_plural = 'лизинговое имущество'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='leasing_assets')
    supplier_name = models.CharField(verbose_name='наименование поставщика/продавца', max_length=512, blank=False, null=False, default='')
    asset_name = models.CharField(verbose_name='наименование, тип, модель', max_length=512, blank=False, null=False, default='')
    asset_spec = models.CharField(verbose_name='спецификация', max_length=512, blank=False, null=False, default='')
    asset_count = models.CharField(verbose_name='количество', max_length=512, blank=False, null=False, default='')
    cost_with_vat = models.CharField(verbose_name='стоимость с НДС', max_length=512, blank=False, null=False, default='')
    supply_term = models.CharField(verbose_name='срок поставки', max_length=512, blank=False, null=False, default='')


class IssueLeasingProdSupplier(models.Model):
    class Meta:
        verbose_name = 'поставщик/продавец предмета лизинга'
        verbose_name_plural = 'поставщики/продавцы предмета лизинга'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='leasing_suppliers')
    supplier_name = models.CharField(verbose_name='наименование поставщика/продавца', max_length=512, blank=False, null=False, default='')
    supplier_head_fio = models.CharField(verbose_name='ФИО руководителя', max_length=512, blank=False, null=False, default='')
    supplier_contact_fio = models.CharField(verbose_name='ФИО контактного лица поставщика/продавца', max_length=512, blank=False, null=False, default='')
    supplier_contacts = models.CharField(verbose_name='контакты', max_length=512, blank=False, null=False, default='')


class IssueLeasingProdPayRule(models.Model):
    class Meta:
        verbose_name = 'порядок и сроки оплаты'
        verbose_name_plural = 'условия и сроки оплаты'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='leasing_pay_rules')
    asset_name = models.CharField(verbose_name='наименование, тип, модель', max_length=512, blank=False, null=False, default='')
    payment_name = models.CharField(verbose_name='наименование платежа', max_length=512, blank=False, null=False, default='')
    payment_size = models.CharField(verbose_name='сумма платежа', max_length=512, blank=False, null=False, default='')
    payment_rule = models.CharField(verbose_name='порядок и срок оплаты', max_length=512, blank=False, null=False, default='')


class IssueBGProdFounderLegal(models.Model):
    class Meta:
        verbose_name = 'учредитель-юрлицо'
        verbose_name_plural = 'учредители-юрлица'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_founders_legal')
    name = models.CharField(verbose_name='наименование', max_length=512, blank=False, null=False, default='')
    add_date = models.CharField(verbose_name='дата внесения', max_length=512, blank=True, null=False, default='')
    additional_business = models.CharField(verbose_name='наличие других видов бизнеса', max_length=512, blank=True, null=False, default='')
    country = models.CharField(verbose_name='страна', max_length=512, blank=True, null=False, default='')
    auth_capital_percentage = models.CharField(verbose_name='доля в уставном капитале', max_length=512, blank=True, null=False, default='')
    legal_address = models.CharField(verbose_name='юридический адрес', max_length=512, blank=True, null=False, default='')


class IssueBGProdFounderPhysical(models.Model):
    class Meta:
        verbose_name = 'учредитель-физлицо'
        verbose_name_plural = 'учредители-физлица'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_founders_physical')
    fio = models.CharField(verbose_name='ФИО', max_length=512, blank=False, null=False, default='')
    add_date = models.CharField(verbose_name='дата внесения', max_length=512, blank=True, null=False, default='')
    additional_business = models.CharField(verbose_name='наличие других видов бизнеса', max_length=512, blank=True, null=False, default='')
    country = models.CharField(verbose_name='страна', max_length=512, blank=True, null=False, default='')
    auth_capital_percentage = models.CharField(verbose_name='доля в уставном капитале', max_length=512, blank=True, null=False, default='')
    address = models.CharField(verbose_name='адрес проживания', max_length=512, blank=True, null=False, default='')
    passport_data = models.CharField(verbose_name='паспортные данные', max_length=512, blank=True, null=False, default='')


class IssuerLicences(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False,
                              related_name='issuer_licences')
    number = models.CharField(verbose_name="номер", max_length=50, null=False, blank=False)
    activity = models.TextField(verbose_name="деятельность", null=False, blank=False, max_length=1024)
    date_from = models.DateField(verbose_name="действительна с", blank=False, null=False)
    date_to = models.DateField(verbose_name="действительна по", blank=True, null=True)
    active = models.BooleanField(verbose_name='активна', default=True)

    def is_active(self):
        return self.active and now().date() < self.date_to

    def __str__(self):
        return self.number

    @classmethod
    def cr(cls, data: dict, issue: Issue):
        active = data.get('statusDescription') == 'Действующая'
        if active:
            number = data.get('officialNum')
            activity = data.get('activity', '\n'.join(data.get('services', [])))
            licence, created = IssuerLicences.objects.get_or_create(issue=issue, number=number, defaults=dict(
                activity=activity,
                date_from=data.get('dateStart'),
                date_to=data.get('dateEnd'),
            ))
            return licence


class IssueProposeFormalizeDocument(models.Model):
    class Meta:
        verbose_name = 'документ для оформления'
        verbose_name_plural = 'документы для оформления'

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='formalize_documents'
    )
    name = models.CharField(verbose_name='название документа', max_length=512, blank=False, null=False, default='')
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issue_formalize_links'
    )


class IssueProposeFinalDocument(models.Model):
    class Meta:
        verbose_name = 'итоговый документ'
        verbose_name_plural = 'итоговые документы'

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='final_documents'
    )
    name = models.CharField(verbose_name='название документа', max_length=512, blank=False, null=False, default='')
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issue_final_links'
    )


class IssueCreditPledge(models.Model):

    class Meta:
        verbose_name = 'обеспечение по заявке'
        verbose_name_plural = 'обеспечения по заявке'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_credit_pledges')
    pledge_title = models.CharField(verbose_name='наименование', max_length=512, blank=False, null=False, default='')
    pledge_type = models.CharField(verbose_name='вид', max_length=32, blank=False, null=False, choices=[
        (consts.CREDIT_PLEDGE_TYPE_DEPOSIT, 'Депозит'),
        (consts.CREDIT_PLEDGE_TYPE_REAL_ESTATE, 'Недвижимость'),
        (consts.CREDIT_PLEDGE_TYPE_OTHER, 'Другое'),
    ])
    cost = models.DecimalField(verbose_name='сумма', max_digits=12, decimal_places=2, blank=True, null=True)


class IssueFactoringBuyer(models.Model):
    class Meta:
        verbose_name = 'покупатель на факторинговое обслуживание'
        verbose_name_plural = 'покупатели на факторинговое обслуживание'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='factoring_buyers')
    name_and_inn = models.CharField(verbose_name='наименование, ИНН', max_length=512, blank=False, null=False, default='')
    avg_monthly_shipments = models.CharField(verbose_name='средние отгрузки за последние 12 месяцев (млн руб. без НДС)', max_length=512, blank=True, null=False, default='')
    operating_pay_deferment_days = models.IntegerField(verbose_name='действующая отсрочка платежа, дней', blank=True, null=True)
    start_work_date = models.CharField(verbose_name='дата начала работы', max_length=512, blank=True, null=False, default='')
    required_credit_limit = models.DecimalField(verbose_name='требуемый кредитный лимит (млн руб. без НДС)', max_digits=12, decimal_places=2, blank=True, null=True)
    debitor_share = models.CharField(verbose_name='доля дебитора', max_length=512, blank=True, null=False, default='')
    average_delay_days = models.IntegerField(verbose_name='средние просрочки за 12 месяцев, дней', blank=True, null=True)
    sales_volume = models.CharField(verbose_name='объем продаж за последние 12 месяцев (млн руб. без НДС)', max_length=512, blank=True, null=False, default='')


class IssueOrgBeneficiaryOwner(models.Model):
    class Meta:
        verbose_name = 'сведения о бенефициарном владельце'
        verbose_name_plural = 'сведения о бенефициарных владельцах'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='org_beneficiary_owners')
    fio = models.CharField(verbose_name='ФИО', max_length=512, blank=False, null=False, default='')
    legal_address = models.CharField(verbose_name='адрес регистрации', max_length=512, blank=False, null=False, default='')
    fact_address = models.CharField(verbose_name='адрес фактического пребывания', max_length=512, blank=False, null=False, default='')
    post_address = models.CharField(verbose_name='почтовый адрес', max_length=512, blank=False, null=False, default='')
    inn_or_snils = models.CharField(verbose_name='ИНН/СНИЛС (при наличии)', max_length=512, blank=False, null=False, default='')
    on_belong_to_pub_persons_info = models.CharField(verbose_name='сведения о принадлежности к публичным лицам', max_length=512, blank=False, null=False, default='')


class IssueOrgBankAccount(models.Model):
    class Meta:
        verbose_name = 'банковский счет принципала'
        verbose_name_plural = 'банковские счета принципала'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='org_bank_accounts')
    name = models.CharField(verbose_name='наименование', max_length=512, blank=False, null=False, default='')
    bik = models.CharField(verbose_name='БИК', max_length=512, blank=False, null=False, default='')
