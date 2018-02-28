import json
import warnings
import os

import feedparser
import requests
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import number_format
from django.utils.functional import cached_property
from django.utils.timezone import now

from marer import consts
from marer.models.base import Document, set_obj_update_time, FormOwnership
from marer.models.finance_org import FinanceOrgProductProposeDocument
from marer.models.issuer import Issuer, IssuerDocument
from marer.products import get_urgency_hours, get_urgency_days, get_finance_products_as_choices, FinanceProduct, get_finance_products, BankGuaranteeProduct
from marer.utils import CustomJSONEncoder, kontur
from marer.utils.issue import calculate_bank_commission, sum_str_format, generate_bg_number, issue_term_in_months, \
    calculate_effective_rate, CalculateUnderwritingCriteria
from marer.utils.morph import MorpherApi
from marer.utils.other import OKOPF_CATALOG, get_tender_info, are_docx_files_identical


__all__ = [
    'Issue', 'IssueDocument', 'IssueClarification', 'IssueMessagesProxy',
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
        (consts.ISSUE_STATUS_CLIENT_REVISION, 'Отправлено клиенту на доработку'),
        (consts.ISSUE_STATUS_RETURNED_FROM_REVISION, 'Возвращена с доработки'),
        (consts.ISSUE_STATUS_CLIENT_AGGREEMENT, 'Отправлено на согласование клиенту'),
        (consts.ISSUE_STATUS_CANCELLED_BY_CLIENT, 'Отменена клиентом'),
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

    @cached_property
    def current_manager(self):
        """
        Возвращает менеджера, работающего в данный момент с заявкой, поле manager в данный момент может быть пустым
        :return:
        """
        from marer.utils.notify import _get_default_manager
        manager = self.manager or self.user.manager
        if not manager:
            warnings.warn('No manager for issue #{issue_id}'.format(issue_id=self.id,))
            manager = _get_default_manager()
        return manager

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
    issuer_oktmo = models.CharField(verbose_name='код ОКТМО заявителя', max_length=32, blank=True, null=False, default='')
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
    tender_placement_type = models.CharField(verbose_name='способ определения поставщика в тендере', max_length=512, blank=True, null=False, default='')
    tender_exec_law = models.CharField(verbose_name='вид банковской гарантии', max_length=32, blank=True, null=True, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
        (consts.TENDER_EXEC_LAW_185_FZ, '185-ФЗ'),
        (consts.TENDER_EXEC_LAW_COMMERCIAL, 'Коммерческий'),
        (consts.TENDER_EXEC_LAW_CUSTOMS, 'Таможенная'),
        (consts.TENDER_EXEC_LAW_VAT, 'Возврат НДС'),
    ])
    tender_publish_date = models.DateField(verbose_name='дата публикации тендера', blank=True, null=True)
    tender_start_cost = models.DecimalField(verbose_name='начальная цена тендера', max_digits=32, decimal_places=2, blank=False, null=False, default=0)
    tender_final_cost = models.DecimalField(verbose_name='конечная цена тендера', max_digits=32, decimal_places=2, blank=True, null=True)

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
    bg_commercial_contract_sum = models.DecimalField(verbose_name='сумма контракта', max_digits=32, decimal_places=2, blank=True, null=True)
    bg_commercial_contract_sign_date = models.DateField(verbose_name='дата заключения договора', blank=True, null=True)
    bg_commercial_contract_end_date = models.DateField(verbose_name='дата завершения договора', blank=True, null=True)

    bg_sum = models.DecimalField(verbose_name='сумма', max_digits=32, decimal_places=2, blank=True, null=True)
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

    curr_year_sales_value = models.DecimalField(verbose_name='Объем продаж за текущий год, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)
    prev_year_sales_value = models.DecimalField(verbose_name='Объем продаж за прошлый год, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)
    curr_year_sales_value_inc_deferment = models.DecimalField(verbose_name='Объем продаж за текущий год, в том числе на условиях отсрочки, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)
    prev_year_sales_value_inc_deferment = models.DecimalField(verbose_name='Объем продаж за прошлый год, в том числе на условиях отсрочки, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)
    curr_year_expected_sales_value = models.DecimalField(verbose_name='Ожидаемые продажи за текущий год по экспорту, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)
    prev_year_expected_sales_value = models.DecimalField(verbose_name='Ожидаемые продажи за прошлый год по экспорту, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)
    curr_year_expected_sales_value_inc_deferment = models.DecimalField(verbose_name='Ожидаемые продажи за текущий год по экспорту в том числе с отсрочкой платежа, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)
    prev_year_expected_sales_value_inc_deferment = models.DecimalField(verbose_name='Ожидаемые продажи за прошлый год по экспорту в том числе с отсрочкой платежа, млн. рублей без НДС', max_digits=32, decimal_places=2, blank=True, null=True)

    formalize_note = models.TextField(verbose_name='подпись к документам для оформления', blank=True, null=False, default='')
    final_note = models.TextField(verbose_name='подпись к итоговым документам', blank=True, null=False, default='')

    balance_code_1300_offset_0 = models.DecimalField('чистые активы за последний отчетный период', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_1600_offset_0 = models.DecimalField('валюта баланса за последний отчетный период', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_2110_offset_0 = models.DecimalField('выручка за последний отчетный период', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_2400_offset_0 = models.DecimalField('прибыль за последний отчетный период', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_1230_offset_0 = models.DecimalField('размер дебиторской задолженности за последний отчетный период', max_digits=32, decimal_places=0, blank=True, null=True)

    balance_code_1300_offset_1 = models.DecimalField('чистые активы за последний год', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_1600_offset_1 = models.DecimalField('валюта баланса за последний год', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_2110_offset_1 = models.DecimalField('выручка за последний год', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_2400_offset_1 = models.DecimalField('прибыль за последний год', max_digits=32, decimal_places=0, blank=True, null=True)

    balance_code_2110_offset_2 = models.DecimalField('выручка за предыдущий год', max_digits=32, decimal_places=0, blank=True, null=True)
    balance_code_2110_analog_offset_0 = models.DecimalField('выручка за аналогичный период', help_text='выручка за период, аналогичный последнему отчетному периоду, в предыдущем году (например 3 кв 2017 и 3 кв 2016)', max_digits=32, decimal_places=0, blank=True, null=True)

    avg_employees_cnt_for_prev_year = models.IntegerField(verbose_name='Средняя численность работников за предшествующий календарный год', blank=False, null=False, default=1)
    issuer_web_site = models.CharField(verbose_name='Web-сайт', max_length=512, blank=True, null=False, default='')
    issuer_accountant_org_or_person = models.CharField(verbose_name='ФИО гл.бухгалтера / наименование организации, осуществляющей ведение бух.учёта', max_length=512, blank=True, null=False, default='')
    issuer_post_address = models.CharField(verbose_name='почтовый адрес заявителя (с индексом) в т.ч. для отправки банковской гарантии', max_length=512, blank=True, null=False, default='')
    bg_is_benefeciary_form = models.NullBooleanField(verbose_name='БГ по форме Бенефециара', blank=True, null=True)
    is_indisputable_charge_off = models.NullBooleanField(verbose_name='право на бесспорное списание', blank=True, null=True)
    tender_contract_subject = models.CharField(verbose_name='предмет контракта', max_length=8192, blank=True, null=False, default='')
    issuer_has_overdue_debts_for_last_180_days = models.NullBooleanField(verbose_name='Наличие просроченной задолженности по всем кредитам за последние 180 дней', blank=True, null=True)
    issuer_overdue_debts_info = models.TextField(verbose_name='Причины и обстоятельства просрочек', blank=True, null=False, default='')
    tax_system = models.CharField(verbose_name='Система налогообложения', max_length=32, blank=True, null=True, choices=[
        (consts.TAX_USN, 'УСН'),
        (consts.TAX_OSN, 'ОСН'),
        (consts.TAX_ENVD, 'ЕНВД'),
        (consts.TAX_ESHD, 'ЕСХД'),
    ])
    agent_comission = models.CharField(verbose_name='Комиссия агента', max_length=512,
                                       blank=True, null=True, default='')

    deal_has_beneficiary = models.NullBooleanField(verbose_name='наличие бенефициара по сделке', blank=True, null=True)
    issuer_bank_relations_term = models.CharField(verbose_name='срок отношений с Банком', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_DEAL_BANK_RELATIONS_TERM_SHORT, 'Краткосрочные'),
        (consts.ISSUE_DEAL_BANK_RELATIONS_TERM_LONG, 'Долгосрочные'),
    ], default=consts.ISSUE_DEAL_BANK_RELATIONS_TERM_LONG)
    issuer_activity_objective = models.CharField(verbose_name='цели финансово-хозяйственной детяельности', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_ISSUER_ACTIVITY_OBJECTIVE_PROFIT_MAKING, 'Получение прибыли'),
        (consts.ISSUE_ISSUER_ACTIVITY_OBJECTIVE_OTHER, 'Иное'),
    ], default=consts.ISSUE_ISSUER_ACTIVITY_OBJECTIVE_PROFIT_MAKING)
    issuer_finance_situation = models.CharField(verbose_name='финансовое положение', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_ISSUER_FINANCE_SITUATION_SATISFIED, 'Удовлетворительное'),
        (consts.ISSUE_ISSUER_FINANCE_SITUATION_UNSATISFIED, 'Неудовлетворительное'),
    ], default=consts.ISSUE_ISSUER_FINANCE_SITUATION_SATISFIED)
    issuer_business_reputation = models.CharField(verbose_name='деловая репутация', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUE_ISSUER_BUSINESS_REPUTATION_POSITIVE, 'Положительная'),
        (consts.ISSUE_ISSUER_BUSINESS_REPUTATION_NOT_PRESENT, 'Отсутствует'),
    ], default=consts.ISSUE_ISSUER_BUSINESS_REPUTATION_POSITIVE)
    issuer_funds_source = models.CharField(verbose_name='источник происхождения денежных средств', max_length=32, blank=True, null=True, choices=[
        (consts.ISSUER_FUNDS_SOURCE_LOAN_FUNDS, 'Заемные средства'),
        (consts.ISSUER_FUNDS_SOURCE_OTHER, 'Иное'),
    ], default=consts.ISSUER_FUNDS_SOURCE_LOAN_FUNDS)

    issuer_org_management_collegial_executive_name = models.CharField(verbose_name='Коллегиальный исполнительный орган: наименование', max_length=512, blank=True, null=False, default='')
    issuer_org_management_collegial_executive_fio = models.CharField(verbose_name='Коллегиальный исполнительный орган: ФИО', max_length=512, blank=True, null=False, default='')
    issuer_org_management_directors_or_supervisory_board_name = models.CharField(verbose_name='Совет директоров (наблюдательный совет): наименование', max_length=512, blank=True, null=False, default='')
    issuer_org_management_directors_or_supervisory_board_fio = models.CharField(verbose_name='Совет директоров (наблюдательный совет): ФИО', max_length=512, blank=True, null=False, default='')
    issuer_org_management_other_name = models.CharField(verbose_name='Иной орган управления организации заявителя: наименование', max_length=512, blank=True, null=False, default='')
    issuer_org_management_other_fio = models.CharField(verbose_name='Иной орган управления организации заявителя: ФИО', max_length=512, blank=True, null=False, default='')

    is_issuer_all_bank_liabilities_less_than_max = models.NullBooleanField('Лимит на Принципала (группу взаимосвязанных Заемщиков) ВСЕХ обязательств Банка менее 18 000 000 руб', blank=True, null=True)
    is_issuer_executed_contracts_on_44_or_223_or_185_fz = models.NullBooleanField('Клиент исполнил не менее 1 контракта в рамках законов № 94-ФЗ, 44-ФЗ, 223-ФЗ, 185-ФЗ (615 ПП)', blank=True, null=True)
    is_issuer_executed_goverment_contract_for_last_3_years = models.NullBooleanField('Наличие исполненного государственного контракта за последние 3 года', blank=True, null=True)
    is_contract_has_prepayment = models.NullBooleanField('Контракт предусматривает выплату аванса', blank=True, null=True)

    is_issuer_executed_contracts_with_comparable_advances = models.NullBooleanField('Клиент исполнял контракты с авансами сопоставимого или большего размера (допустимое отклонение в меньшую сторону не более 50 % включительно)', blank=True, null=True)
    is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz = models.NullBooleanField('Факт исполнения не менее 5 контрактов, заключенных в рамках законов № 44-ФЗ (включая № 94-ФЗ), 223-ФЗ, 185-ФЗ (615 ПП)', blank=True, null=True)
    is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs = models.NullBooleanField('Выручка Клиента за последний завершенный год не менее, чем в 5 раз превышает сумму запрашиваемой и действующих в Банке гарантий', blank=True, null=True)
    is_issuer_has_garantor_for_advance_related_requirements = models.NullBooleanField('Наличие Поручителя юридического лица удовлетворяющим одному из предыдущих трех условий', blank=True, null=True)

    is_contract_price_reduction_lower_than_50_pct_on_supply_contract = models.NullBooleanField('Снижение цены Контракта менее 50% если предмет контракта «Поставка»', blank=True, null=True)
    is_positive_security_department_conclusion = models.NullBooleanField('Наличие положительного Заключения СБ', blank=True, null=True)
    is_positive_lawyers_department_conclusion = models.NullBooleanField('Наличие положительного Заключения ПУ (в соответствии с Приказом по проверке ПУ)', blank=True, null=True)
    is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets = models.NullBooleanField('Отсутствие информации об исполнительных производствах Приницпала его Участников на сумму более 20% чистых активов Клиента', blank=True, null=True)
    is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets = models.NullBooleanField('Отсутствие информации о судебных разбирательствах Клиента в качестве ответчика (за исключением закрытых) на сумму более 30% чистых активов Клиента', blank=True, null=True)
    is_need_to_check_real_of_issuer_activity = models.NullBooleanField('Есть необходимость оценки реальности деятельности', blank=False, null=False, default=False)
    is_real_of_issuer_activity_confirms = models.NullBooleanField('Реальность деятельности подтверждается', blank=True, null=True)
    is_contract_corresponds_issuer_activity = models.IntegerField('Соответствие контракта профилю деятельности клиента', choices=[
        (None, 'Неизвестно'),
        (1, 'Да — 1 балл рейтинга'),
        (2, 'Да — 2 балла рейтинга'),
        (4, 'Да — 4 балла рейтинга'),
        (6, 'Нет — 6 баллов рейтинга'),
    ], blank=True, null=True)

    total_bank_liabilities_vol = models.DecimalField(verbose_name='объем обязательств банка', max_digits=32, decimal_places=2, blank=True, null=True)

    contract_advance_requirements_fails = models.NullBooleanField('Не выполняются требования к авансированию (при наличии в контракте аванса)', blank=True, null=True)
    is_issuer_has_bad_credit_history = models.NullBooleanField('Наличие текущей просроченной ссудной задолженности и отрицательной кредитной истории в кредитных организациях', blank=True, null=True)
    is_issuer_has_blocked_bank_account = models.NullBooleanField('Наличие информации о блокировке счетов', blank=True, null=True)

    persons_can_acts_as_issuer_and_perms_term_info = models.TextField(verbose_name='Сведения о физических лицах, имеющих право действовать от имени Принципала без доверенности, срок окончания полномочий', blank=True, null=False, default='')
    lawyers_dep_recommendations = models.TextField(
        verbose_name='Рекомендации',
        help_text='Сотрудником правового управления должны быть оценена актуальность и достаточность предоставленных '
                  'документов (устав и изменения к нему, документы, подтверждающие полномочия руководителя (включая '
                  'сроки), соблюдение процедуры одобрения сделок (если подлежат одобрению по специальным основаниям). '
                  'Обращено внимание на соблюдение процессуальных процедур при оформлении уставных документов.',
        blank=True, null=False, default='')
    final_documents_operations_management_conclusion_override = models.NullBooleanField('Принудительное решение УРДО в спорных ситуациях', blank=True, null=True)

    total_credit_pay_term_expiration_events = models.IntegerField('Количество случаев просрочки', blank=True, null=True)
    total_credit_pay_term_overdue_days = models.IntegerField('Совокупное количество дней просрочки', blank=True, null=True)

    validity_of_shareholders_participants_issuer_head_passports = models.NullBooleanField('Действительность паспортов акционеров/участников, руководителя Принципала', blank=True, null=True)

    @property
    def humanized_validity_of_shareholders_participants_issuer_head_passports(self):
        return 'Да' if self.validity_of_shareholders_participants_issuer_head_passports else 'Нет'

    issuer_fact_address_check = models.NullBooleanField(
        'Проверка адреса, заявленного Принципалом как фактического',
        help_text='Проверка документов, подтверждающих основание нахождения по адресу, заявленному '
             'как фактический, проверка компании арендодателя (как действующего  юридического '
             'лица, так и индивидуального предпринимателя) на наличие государственной '
             'регистрации в налоговых органах',
        blank=True, null=True
    )

    @property
    def humanized_issuer_fact_address_check(self):
        return 'Да' if self.issuer_fact_address_check else 'Нет'

    issuer_shareholders_participants_or_self_court_cases_info = models.TextField(verbose_name='Данные о Принципале, его участниках в базе данных исполнительных производств', blank=True, null=False, default='')
    issuer_courts_cases_as_defendant_and_its_acts_info = models.TextField(verbose_name='Информация о судебных разбирательствах Принципала (в качестве ответчика), о находящихся в суде делах и принятых по ним судебным актам', blank=True, null=False, default='')

    is_absent_info_about_court_cases_on_ifns_or_bankrupts_or_contracts_as_defendant = models.NullBooleanField('Отсутствие наличия информации о судебных разбирательствах по искам, ответчиком по которым является Принципал: по судебным разбирательствам с ИФНС, по заявлениям о признании Принципала несостоятельным (банкротом), по искам неисполнения государственных контрактов', blank=True, null=True)

    @property
    def humanized_is_absent_info_about_court_cases_on_ifns_or_bankrupts_or_contracts_as_defendant(self):
        return 'Да' if self.is_absent_info_about_court_cases_on_ifns_or_bankrupts_or_contracts_as_defendant else 'Нет'

    is_absent_info_about_prev_convictions_on_issuer_head_or_shareholders_or_participants_or_guarantor = models.NullBooleanField('Отсутствие судимостей в отношении физических лиц (генеральный директор, участники юридического лица (c наибольшей долей участия, Поручитель)', blank=True, null=True)

    @property
    def humanized_is_absent_info_about_prev_convictions_on_issuer_head_or_shareholders_or_participants_or_guarantor(self):
        return 'Да' if self.is_absent_info_about_prev_convictions_on_issuer_head_or_shareholders_or_participants_or_guarantor else 'Нет'

    has_issuer_bad_info_on_credit_history = models.NullBooleanField('Наличие негативной информации по кредитной истории', blank=True, null=True)
    has_issuer_bad_info_on_bank_abs = models.NullBooleanField('Наличие негативной информации по АБС Банка', blank=True, null=True)
    has_issuer_bad_info_on_kontur_and_spark = models.NullBooleanField('Наличие негативной информации в информационной системе "Контур-фокус" / "Спарк"', blank=True, null=True)
    has_issuer_bad_info_on_fns_site = models.NullBooleanField('Наличие негативной информации на сайте ФНС России', blank=True, null=True)
    has_issuer_bad_info_on_ros_fin_monitoring = models.NullBooleanField('Наличие негативной информации на сайте Росфинмониторинга', blank=True, null=True)
    has_issuer_bad_info_on_arbitr_ru_site = models.NullBooleanField('Наличие негативной информации на сайте Арбитражного суда РФ', blank=True, null=True)
    has_issuer_bad_info_on_sudrf_ru = models.NullBooleanField('Наличие негативной информации на сайтах судов общей юрисдикции (мировых судов)', blank=True, null=True)
    has_issuer_bad_info_on_fssp = models.NullBooleanField('Наличие негативной информации на сайте ФССП  России', blank=True, null=True)
    has_issuer_bad_info_on_public_sources_sites = models.NullBooleanField('Получение информации о юридическом лице из открытых интернет источников', blank=True, null=True)
    has_issuer_bad_info_on_persons_have_impact_on_issue_activity = models.NullBooleanField('Наличие негативной информации по лицам, имеющим влияние на деятельность юридического лица ', blank=True, null=True)
    has_issuer_bad_info_on_guarantors = models.NullBooleanField('Наличие негативной информации по поручителям', blank=True, null=True)
    has_issuer_bad_info_on_security_db = models.NullBooleanField('Наличие негативной информации в информационной базе ДБ Банка', blank=True, null=True)

    @property
    def humanized_is_issuer_has_blocked_bank_account(self):
        if self.is_issuer_has_blocked_bank_account is True:
            return 'Да'
        elif self.is_issuer_has_blocked_bank_account is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_contract_advance_requirements_fails(self):
        if self.contract_advance_requirements_fails is True:
            return 'Да'
        elif self.contract_advance_requirements_fails is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_security_db(self):
        if self.has_issuer_bad_info_on_security_db is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_security_db is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_guarantors(self):
        if self.has_issuer_bad_info_on_guarantors is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_guarantors is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_persons_have_impact_on_issue_activity(self):
        if self.has_issuer_bad_info_on_persons_have_impact_on_issue_activity is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_persons_have_impact_on_issue_activity is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_public_sources_sites(self):
        if self.has_issuer_bad_info_on_public_sources_sites is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_public_sources_sites is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_fssp(self):
        if self.has_issuer_bad_info_on_fssp is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_fssp is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_sudrf_ru(self):
        if self.has_issuer_bad_info_on_sudrf_ru is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_sudrf_ru is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_arbitr_ru_site(self):
        if self.has_issuer_bad_info_on_arbitr_ru_site is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_arbitr_ru_site is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_ros_fin_monitoring(self):
        if self.has_issuer_bad_info_on_ros_fin_monitoring is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_ros_fin_monitoring is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_fns_site(self):
        if self.has_issuer_bad_info_on_fns_site is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_fns_site is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_kontur_and_spark(self):
        if self.has_issuer_bad_info_on_kontur_and_spark is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_kontur_and_spark is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_bank_abs(self):
        if self.has_issuer_bad_info_on_bank_abs is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_bank_abs is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_has_issuer_bad_info_on_credit_history(self):
        if self.has_issuer_bad_info_on_credit_history is True:
            return 'Да'
        elif self.has_issuer_bad_info_on_credit_history is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_is_issuer_has_bad_credit_history(self):
        if self.is_issuer_has_bad_credit_history is True:
            return 'Да'
        elif self.is_issuer_has_bad_credit_history is False:
            return 'Нет'
        else:
            return '—'

    @property
    def humanized_is_issuer_all_bank_liabilities_less_than_max(self):
        if self.is_issuer_all_bank_liabilities_less_than_max is True:
            return 'Да'
        if self.is_issuer_all_bank_liabilities_less_than_max is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_issuer_executed_contracts_on_44_or_223_or_185_fz(self):
        if self.is_issuer_executed_contracts_on_44_or_223_or_185_fz is True:
            return 'Да'
        if self.is_issuer_executed_contracts_on_44_or_223_or_185_fz is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_not_issuer_executed_contracts_on_44_or_223_or_185_fz(self):
        return 'Нет' if self.is_issuer_executed_contracts_on_44_or_223_or_185_fz else 'Да'

    @property
    def humanized_is_issuer_executed_goverment_contract_for_last_3_years(self):
        if self.is_issuer_executed_goverment_contract_for_last_3_years is True:
            return 'Да'
        if self.is_issuer_executed_goverment_contract_for_last_3_years is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_negative_net_assets_for_last_quarter(self):
        return 'Да' if self.balance_code_1300_offset_0 < 0 else 'Нет'

    @property
    def humanized_is_issuer_in_blacklisted_region(self):
        return 'Да' if self.is_issuer_in_blacklisted_region else 'Нет'

    @property
    def humanized_is_beneficiary_in_blacklisted_region(self):
        return 'Да' if self.is_beneficiary_in_blacklisted_region else 'Нет'

    @property
    def humanized_is_bg_term_more_30_months(self):
        return 'Да' if issue_term_in_months(self.bg_start_date, self.bg_end_date) > 30 else 'Нет'

    @property
    def humanized_is_bg_limit_exceeded_max(self):
        return 'Да' if self.bg_sum > 18000000 else 'Нет'

    @property
    def issuer_presence_in_unfair_suppliers_registry(self):
        kontur_principal_analytics_data = kontur.analytics(inn=self.issuer_inn, ogrn=self.issuer_ogrn).get('analytics', {})
        return kontur_principal_analytics_data.get('m4001', False)

    @property
    def humanized_issuer_is_not_present_in_unfair_suppliers_registry(self):
        return 'Да' if not self.issuer_presence_in_unfair_suppliers_registry else 'Нет'

    @property
    def is_issuer_liquidating_or_bankrupt(self):
        kontur_principal_analytics_data = kontur.analytics(inn=self.issuer_inn, ogrn=self.issuer_ogrn).get('analytics', {})
        return kontur_principal_analytics_data.get('m7014', False)

    @property
    def humanized_is_not_issuer_liquidating_or_bankrupt(self):
        return 'Да' if not self.is_issuer_liquidating_or_bankrupt else 'Нет'
    
    @property
    def is_issuer_present_in_terrorists_list(self):
        url = 'http://www.fedsfm.ru/TerroristSearch'
        json = dict(pageLength=50, rowIndex=0, searchText=self.issuer_inn)
        result = requests.post(url, json=json).json()
        if result.get('IsError', False) and result.get('recordsTotal', 1) == 0:
            return False
        elif result.get('IsError', False) and result.get('recordsTotal', 1) > 0:
            return True

    @property
    def humanized_is_issuer_not_present_in_terrorists_list(self):
        return 'Да' if not self.is_issuer_present_in_terrorists_list else 'Нет'


    @property
    def humanized_issuer_presence_in_unfair_suppliers_registry(self):
        return 'Да' if self.issuer_presence_in_unfair_suppliers_registry else 'Нет'

    @property
    def humanized_is_contract_has_prepayment(self):
        if self.is_contract_has_prepayment is True:
            return 'Да'
        if self.is_contract_has_prepayment is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_issuer_executed_contracts_with_comparable_advances(self):
        if not self.tender_has_prepayment:
            return ' '
        if self.is_issuer_executed_contracts_with_comparable_advances is True:
            return 'Да'
        if self.is_issuer_executed_contracts_with_comparable_advances is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz(self):
        if not self.tender_has_prepayment:
            return ' '
        if self.is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz is True:
            return 'Да'
        if self.is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs(self):
        if not self.tender_has_prepayment:
            return ' '
        if self.is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs is True:
            return 'Да'
        if self.is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_issuer_has_garantor_for_advance_related_requirements(self):
        if not self.tender_has_prepayment:
            return ' '
        if self.is_issuer_has_garantor_for_advance_related_requirements is True:
            return 'Да'
        if self.is_issuer_has_garantor_for_advance_related_requirements is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_contract_price_reduction_lower_than_50_pct_on_supply_contract(self):
        if self.is_contract_price_reduction_lower_than_50_pct_on_supply_contract is True:
            return 'Да'
        if self.is_contract_price_reduction_lower_than_50_pct_on_supply_contract is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_positive_security_department_conclusion(self):
        if self.is_positive_security_department_conclusion is True:
            return 'Да'
        if self.is_positive_security_department_conclusion is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_positive_lawyers_department_conclusion(self):
        if self.is_positive_lawyers_department_conclusion is True:
            return 'Да'
        if self.is_positive_lawyers_department_conclusion is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets(self):
        if self.is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets is True:
            return 'Да'
        if self.is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets(self):
        if self.is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets is True:
            return 'Да'
        if self.is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_need_to_check_real_of_issuer_activity(self):
        if self.is_need_to_check_real_of_issuer_activity is True:
            return 'Да'
        if self.is_need_to_check_real_of_issuer_activity is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_real_of_issuer_activity_confirms(self):
        if self.is_real_of_issuer_activity_confirms is True:
            return 'Да'
        if self.is_real_of_issuer_activity_confirms is False:
            return 'Нет'
        return '—'

    @property
    def humanized_is_contract_corresponds_issuer_activity(self):
        if self.is_contract_corresponds_issuer_activity is None:
            return '—'
        elif self.is_contract_corresponds_issuer_activity < 6:
            return 'Да'
        elif self.is_contract_corresponds_issuer_activity == 6:
            return 'Нет'
        return '—'

    @property
    def final_documents_operations_management_conclusion(self):
        if self.bg_sum < 1500000:
            strong_checks = []
            variative_checks = []
            # 1 Дата регистрации Клиента более 6 мес.
            strong_checks.append(self.is_org_registered_more_than_6_months_ago)
            # 2 Лимит на Принципала (группу взаимосвязанных Заемщиков) ВСЕХ обязательств Банка менее 18 000 000 руб.
            strong_checks.append(self.is_issuer_all_bank_liabilities_less_than_max)
            # 3 Клиент исполнил не менее 1 контракта в рамках законов № 94-ФЗ, 44-ФЗ, 223-ФЗ, 185-ФЗ (615 ПП).
            strong_checks.append(self.is_issuer_executed_contracts_on_44_or_223_or_185_fz)
            # 4 Наличие исполненного  государственного контракта за последние 3  года.
            strong_checks.append(self.is_issuer_executed_goverment_contract_for_last_3_years)

            # 5 При выдачи БГ по контракту предусматривающей выплату аванса
            if self.tender_has_prepayment:
                prepayment_checks = []
                # 5.1 Клиент исполнял контракты с авансами сопоставимого или большего размера (допустимое отклонение в меньшую сторону не более 50 % включительно).
                prepayment_checks.append(self.is_issuer_executed_contracts_with_comparable_advances)
                # 5.2 Факт исполнения не менее 5 контрактов, заключенных в рамках законов № 44-ФЗ (включая № 94-ФЗ), 223-ФЗ, 185-ФЗ (615 ПП);
                prepayment_checks.append(self.is_issuer_executed_gte_5_contracts_on_44_or_223_or_185_fz)
                # 5.3 Выручка Клиента за последний завершенный год не менее, чем в 5 раз превышает сумму запрашиваемой и действующих в Банке гарантий
                prepayment_checks.append(self.is_issuer_last_year_revenue_higher_in_5_times_than_all_bank_bgs)
                # 5.4 Наличие Поручителя юридического лица удовлетворяющим одному из условий пп. 5.1, 5.2, 5.3.
                prepayment_checks.append(self.is_issuer_has_garantor_for_advance_related_requirements)
                prepayment_checks = [bool(check) for check in prepayment_checks]
                strong_checks.append(True in prepayment_checks)

            # 6 Величина чистых активов за последний завершенный квартал больше уставного капитала (только для организаций, предоставивших отчетность по форме № 1 и №2).
            strong_checks.append(self.last_account_period_net_assets_great_than_authorized_capital)
            # 7 Деятельность Клиента в течение Последнего завершенного года являлась прибыльной.
            strong_checks.append(self.balance_code_2400_offset_1 > 0)
            # 8 Деятельность Клиента за последний отчетный период  является прибыльной.
            strong_checks.append(self.balance_code_2400_offset_0 > 0)
            # 9 Снижение цены Контракта менее 50% если предмет контракта «Поставка»
            strong_checks.append(self.is_contract_price_reduction_lower_than_50_pct_on_supply_contract)
            # 10 Финансовое положение хорошое (Расчет производится согласно Положения о предоставлении банковских гарантий ПАО «БАНК СГБ» в рамках продукта «Экспресс - гарантии).
            strong_checks.append(self.scoring_rating_sum <= 25)
            # 11 Клиент не находится в регионе, с которым Банк не работает
            strong_checks.append(self.is_issuer_in_blacklisted_region is False)
            # 12 Бенефициар не находится в регионе, с которым Банк не работает
            strong_checks.append(self.is_beneficiary_in_blacklisted_region is False)
            # 13 Наличие положительного Заключения СБ
            strong_checks.append(self.is_positive_security_department_conclusion)
            # 14 Наличие положительного Заключения ПУ (в соответствии с Приказом по проверке ПУ)
            strong_checks.append(self.is_positive_lawyers_department_conclusion)
            strong_checks = [bool(check) for check in strong_checks]
            if False in strong_checks:
                return False

            # 15* Отсутствие информации об исполнительных производствах Приницпала его Участников на сумму более 20% чистых активов (ЧА) Клиента. ЧА – сумма 3 раздела Баланса «Капитал и Резервы» на последнюю отчетную дату, за исключением исполнительных производств по госконтрактам.
            variative_checks.append(self.is_absent_info_about_court_acts_for_more_than_20_pct_of_net_assets)
            # 16* Отсутствие информации о судебных разбирательствах Клиента в качестве ответчика (за исключением закрытых) на сумму более 30% чистых активов (ЧА) Клиента. ЧА – сумма 3 раздела Баланса «Капитал и Резервы» на последнюю отчетную дату, за исключением судебных разбирательств в качестве ответчика  по госконтрактам.
            variative_checks.append(self.is_absent_info_about_legal_proceedings_as_defendant_for_more_than_30_pct_of_net_assets)
            variative_checks = [bool(check) for check in variative_checks]
            return not False in variative_checks or self.final_documents_operations_management_conclusion_override
        else:
            strong_checks = []

            # 1 Дата регистрации Клиента менее 6 мес.
            strong_checks.append(self.is_org_registered_more_than_6_months_ago)
            # 2 Клиент не исполнял контракты, заключенный с организацией, заключающей контракты в рамках законов № 94-ФЗ, 44-ФЗ, 223-ФЗ, 185-ФЗ.
            strong_checks.append(self.is_issuer_executed_contracts_on_44_or_223_or_185_fz)
            # 3 Отрицательная величина чистых активов за последний завершенный квартал (только для организаций, предоставивших отчетность по форме № 1 и №2).
            strong_checks.append(self.balance_code_1300_offset_0 >= 0)
            # 4 Деятельность Клиента в течение Последнего завершенного года и последнего завершенного квартала являлась убыточной.
            strong_checks.append(self.balance_code_2400_offset_1 > 0)
            # 5 Клиент не находится в регионе, с которым Банк не работает
            strong_checks.append(self.is_issuer_in_blacklisted_region is False)
            # 6 Бенефициар не находится в регионе, с которым Банк не работает
            strong_checks.append(self.is_beneficiary_in_blacklisted_region is False)
            # 7 Срок БГ более 30 мес.
            strong_checks.append(issue_term_in_months(self.bg_start_date, self.bg_end_date) <= 30)
            # 8 Лимит БГ на клиента превышает 15 млн.руб. (в т.ч. при запросе тендерной БГ)
            strong_checks.append(self.bg_sum <= 18000000)
            # 9 Не выполняются требования к авансированию (при наличии в контракте аванса)
            strong_checks.append(self.contract_advance_requirements_fails is False)
            # 10 Наличие текущей просроченной ссудной задолженности и отрицательной кредитной истории в кредитных организациях.
            strong_checks.append(self.is_issuer_has_bad_credit_history is False)
            # 11 Наличие Клиента в реестре недобросовестных поставщиков.
            strong_checks.append(self.issuer_presence_in_unfair_suppliers_registry is False)
            # 12 Наличие информации о блокировке счетов
            strong_checks.append(self.is_issuer_has_blocked_bank_account is False)
            # 13 Финансовое положение средние или плохое
            strong_checks.append(self.scoring_rating_sum <= 25)
            strong_checks = [bool(check) for check in strong_checks]
            if False in strong_checks:
                return False
            else:
                return True

    @property
    def humanized_final_documents_operations_management_conclusion(self):
        if self.final_documents_operations_management_conclusion is True:
            return 'Положительное'
        if self.final_documents_operations_management_conclusion is False:
            return 'Отрицательное'
        if self.final_documents_operations_management_conclusion is None:
            return 'Не определено'

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
    lawyers_dep_conclusion_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lawyers_dep_conclusion_docs_links'
    )

    sec_dep_conclusion_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sec_dep_conclusion_docs_links'
    )
    bg_contract_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bg_contract_doc',
        verbose_name='Договор'
    )
    bg_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bg_doc',
        verbose_name='Проект'
    )
    contract_of_guarantee = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contract_of_guaranties',
        verbose_name='Договор поручительства'
    )
    transfer_acceptance_act = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_acceptance_acts_links',
        verbose_name='Акт',
    )
    additional_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='additional_doc'
    )
    underwriting_criteria_doc = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='underwriting_criteria_doc'
    )
    underwriting_criteria_score = models.FloatField(verbose_name='Оценка по критериям андеррайтинга', blank=True, null=True)
    approval_and_change_sheet = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_and_change_sheet'
    )
    payment_of_fee = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payment_of_fee'
    )
    
    similar_contract_sum = models.FloatField(blank=True, null=True, default=0)
    biggest_contract_sum = models.FloatField(blank=True, null=True, default=0)
    similar_contract_date = models.DateField(blank=True, null=True)
    has_fines_on_zakupki_gov_ru = models.BooleanField(default=False, help_text='наличие штрафов по контрактом, отраженных на сайте Госзакупок')
    has_arbitration = models.BooleanField(default=False, help_text='наличие арбитражей по нарушениям выполнения условий гос. контрактов')

    def get_urgency_for_user(self, user):
        messages = list(self.clarification_messages.all().order_by('-id'))
        if messages:
            last_message = messages[0]
            is_manager_message_last = False
            if last_message.user != user:
                is_manager_message_last = True
            if is_manager_message_last and self.bg_sum < 1500000:
                time = get_urgency_hours(last_message.created_at)
                if time > 5:
                    return '<span class="glyphicon glyphicon-time text-danger"></span>'
                else:
                    return '<span class="glyphicon glyphicon-time text-primary"></span>'
            elif is_manager_message_last and self.bg_sum >= 1500000:
                d = get_urgency_days(last_message.created_at)
                if get_urgency_days(last_message.created_at) > 0:
                    return '<span class="glyphicon glyphicon-time text-danger"></span>'
                else:
                    return '<span class="glyphicon glyphicon-time text-primary"></span>'
            else:
                return '<span class="glyphicon glyphicon-time text-muted"></span>'
        else:
            return '<span class="glyphicon glyphicon-time text-muted"></span>'

    def get_last_comment_for_user(self, user):
        if self.status == consts.ISSUE_STATUS_REVIEW:
            messages = list(self.clarification_messages.all().order_by('-id'))
            if messages:
                last_message = messages[0].message
                count_messages_before = 0
                for message in messages[::-1]:
                    if message.user != user:
                        count_messages_before += 1
                if count_messages_before > 0:
                    return '%s <span class="badge">%s</span>' % (last_message, count_messages_before)
                else:
                    return '%s' % last_message
        return '-'

    @cached_property
    def finished_contracts_count(self):
        url = 'http://zakupki.gov.ru/epz/contract/extendedsearch/rss?openMode=USE_DEFAULT_PARAMS&pageNumber=1&sortDirection=false&recordsPerPage=_50&sortBy=PO_DATE_OBNOVLENIJA&fz44=on&fz94=on&priceFrom=0&priceTo=200000000000&advancePercentFrom=hint&advancePercentTo=hint&contractStageList_1=on&contractStageList=1&supplierTitle=%s' % self.issuer_inn
        data = feedparser.parse(url)
        fz_44_contracts = len(data['entries'])
        url = 'http://zakupki.gov.ru/epz/contractfz223/extendedSearch/rss?morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_10&statuses_1=on&statuses=1&supplierTitle=%s&currencyId=1&sortBy=BY_UPDATE_DATE' % self.issuer_inn
        data = feedparser.parse(url)
        fz_223_contracts = len(data['entries'])
        return fz_44_contracts + fz_223_contracts

    @cached_property
    def passed_prescoring(self):
        return self.auto_bank_commission and self.check_stop_factors_validity

    @cached_property
    def auto_bank_commission(self):
        return calculate_bank_commission(
            self.bg_start_date,
            self.bg_end_date,
            self.bg_sum,
            self.bg_is_benefeciary_form,
            self.bg_type,
            self.tender_exec_law,
            self.tender_has_prepayment,
        )

    @cached_property
    def agent_effective_rate(self):
        return calculate_effective_rate(
            self.bg_sum,
            self.agent_comission,
            self.bg_start_date,
            self.bg_end_date
        )

    @cached_property
    def agent_commission_passed(self):
        if self.agent_comission:
            if int(self.agent_comission) > int(0.7 * float(self.auto_bank_commission)) and self.agent_effective_rate > 2.7:
                return True
            else:
                return False

    @cached_property
    def bank_commission(self):
        if self.agent_comission and self.agent_commission_passed:
            return self.agent_comission
        else:
            return self.auto_bank_commission

    @property
    def humanized_id(self):
        if self.id:
            return str(self.id).zfill(10)
        else:
            return 'БЕЗ НОМЕРА'

    @property
    def humanized_custom_tender_contract_sum(self):
        if self.tender_final_cost:
            return '{} рублей'.format(self.tender_final_cost)
        else:
            return 'тендер не разыгран'

    @property
    def tender_cost_reduction(self):
        if self.tender_start_cost and self.tender_final_cost:
            return round((1 - self.tender_final_cost / self.tender_start_cost) * 100, 0)

    @property
    def humanized_custom_tender_cost_reduction(self):
        if self.tender_cost_reduction:
            return '{}%'.format(self.tender_cost_reduction)
        else:
            return '—'

    @property
    def humanized_custom_if_need_additionally_contract_guarantee_issue_with_cost(self):
        if self.bg_type == consts.BG_TYPE_APPLICATION_ENSURE and self.tender_gos_number:
            tender_info = get_tender_info(self.tender_gos_number)
            if tender_info and type(tender_info) == dict:
                contract_ensure_cost = tender_info['contract_execution_ensure_cost']
                if contract_ensure_cost and contract_ensure_cost > 0:
                    template_text = 'Одновременно принимается решение о выдачи гарантии ' \
                                    'исполнения обязательств по контракту:' \
                                    '\nСумма гарантии: {} рублей'
                    return template_text.format(contract_ensure_cost)
        return ' '

    @property
    def scoring_issuer_profitability(self):
        try:
            coeff = (self.balance_code_2400_offset_1 / self.balance_code_2110_offset_1) * 100
        except ArithmeticError:
            return 3
        if coeff < 0.5:
            return 4
        elif 0.5 <= coeff < 1:
            return 3
        elif 1 <= coeff < 3:
            return 2
        elif 3 <= coeff:
            return 1

    @property
    def scoring_revenue_reduction(self):
        try:
            code_2110_offset_2 = self.balance_code_2110_offset_2 or 0
            coeff = (self.balance_code_2110_offset_1 / code_2110_offset_2) * 100
        except ArithmeticError:
            return 3
        if coeff < 75:
            return 4
        elif 75 <= coeff < 100:
            return 3
        elif 100 <= coeff < 110:
            return 2
        elif 110 <= coeff:
            return 1

    @property
    def scoring_own_funds_ensurance(self):
        try:
            coeff = (self.balance_code_1300_offset_1 / self.balance_code_1600_offset_1) * 100
        except ArithmeticError:
            return 3
        if coeff <= 5:
            return 4
        elif 5 <= coeff <= 15:
            return 3
        elif 15 <= coeff <= 30:
            return 2
        elif 30 <= coeff:
            return 1

    @property
    def scoring_current_profit(self):
        return 1 if self.balance_code_2400_offset_0 > 0 else 2

    @property
    def scoring_finished_contracts_count(self):
        coeff = self.finished_contracts_count
        if coeff <= 1:
            return 6
        elif 2 <= coeff <= 4:
            return 3
        elif 5 <= coeff <= 7:
            return 2
        elif 7 < coeff:
            return 1

    @property
    def scoring_credit_history(self):
        if self.bg_sum < 1500000:
            return 3

        if self.total_credit_pay_term_expiration_events == 0 and self.total_credit_pay_term_overdue_days == 0:
            return 1
        issuer_has_no_credit_history = self.total_credit_pay_term_expiration_events is None and self.total_credit_pay_term_overdue_days is None
        if issuer_has_no_credit_history or (self.total_credit_pay_term_expiration_events == 1 and self.total_credit_pay_term_overdue_days <= 5):
            return 2
        if self.total_credit_pay_term_expiration_events <= 2:
            return 3
        return 4

    @property
    def humanized_total_credit_pay_term_expiration_events(self):
        return self.total_credit_pay_term_expiration_events or '—'

    @property
    def humanized_total_credit_pay_term_overdue_days(self):
        return self.total_credit_pay_term_overdue_days or '—'

    @property
    def scoring_rating_sum(self):
        return (
            self.scoring_current_profit
            + self.scoring_issuer_profitability
            + self.scoring_own_funds_ensurance
            + self.scoring_revenue_reduction
            + self.scoring_finished_contracts_count
            + self.scoring_credit_history
            + self.is_contract_corresponds_issuer_activity
        )

    @property
    def scoring_credit_rating(self):
        coeff = self.scoring_rating_sum
        if coeff <= 14 and self.bg_sum > 5000000:
            return 'Asgb'
        elif 15 <= coeff <= 25 and self.bg_sum > 5000000:
            return 'Bsgb'
        elif coeff <= 14 and 1500000 < self.bg_sum <= 5000000:
            return 'Esgb'
        elif 15 <= coeff <= 25 and 1500000 < self.bg_sum <= 5000000:
            return 'E2sgb'
        elif coeff <= 14 and self.bg_sum <= 1500000:
            return 'Fsgb'
        elif 15 <= coeff <= 25 and self.bg_sum <= 1500000:
            return 'F2sgb'
        elif 26 <= coeff <= 30:
            return 'Csgb'
        elif 31 <= coeff:
            return 'Dsgb'


    @property
    def client_finance_situation(self):
        coeff = self.scoring_rating_sum
        if coeff <= 25:
            return 'Хорошее'
        elif 26 <= coeff <= 30:
            return 'Среднее'
        elif 31 <= coeff:
            return 'Плохое'

    @property
    def humanized_is_client_finance_situation_good(self):
        return 'Да' if self.scoring_rating_sum <= 25 else 'Нет'

    @property
    def humanized_is_not_client_finance_situation_good(self):
        return 'Да' if not self.scoring_rating_sum <= 25 else 'Нет'

    @property
    def last_account_period_net_assets_great_than_authorized_capital(self):
        details = kontur.egrDetails(inn=self.issuer_inn, ogrn=self.issuer_ogrn)
        authorized_capital = 0
        if details and details.get('UL', False):
            authorized_capital = details.get('UL', {}).get('statedCapital', {}).get('sum', 0)
        return self.balance_code_1300_offset_0 * 1000 > authorized_capital

    @property
    def humanized_last_account_period_net_assets_great_than_authorized_capital(self):
        return 'Да' if self.last_account_period_net_assets_great_than_authorized_capital else 'Нет'

    @property
    def humanized_sum(self):
        if self.bg_sum:
            fmt_sum = number_format(self.bg_sum, force_grouping=True)
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
    def humanized_created_at(self):
        return self.created_at.strftime('%d.%m.%Y') if self.created_at else ''

    @property
    def humanized_created_at_with_quotes_and_month_as_word(self):
        months = [
            None,  # month number 0, in dates starts from 1
            'января',
            'февраля',
            'марта',
            'апреля',
            'мая',
            'июня',
            'июля',
            'августа',
            'сентября',
            'октября',
            'ноября',
            'декабря',
        ]
        return self.created_at.strftime('«%d» {} %Y'.format(months[self.created_at.month])) if self.created_at else ''

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
    def humanized_issuer_head_birthday(self):
        return self.issuer_head_birthday.strftime('%d.%m.%Y') if self.issuer_head_birthday else ''

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
    def management_collegial_org_name(self):
        return '\n'.join(list(self.org_management_collegial.all().values_list('org_name', flat=True)))

    @cached_property
    def management_collegial_fio(self):
        return '\n'.join(list(self.org_management_collegial.all().values_list('fio', flat=True)))

    @cached_property
    def management_directors_org_name(self):
        return '\n'.join(list(self.org_management_directors.all().values_list('org_name', flat=True)))

    @cached_property
    def management_directors_fio(self):
        return '\n'.join(list(self.org_management_directors.all().values_list('fio', flat=True)))

    @cached_property
    def management_others_org_name(self):
        return '\n'.join(list(self.org_management_others.all().values_list('org_name', flat=True)))

    @cached_property
    def management_others_fio(self):
        return '\n'.join(list(self.org_management_others.all().values_list('fio', flat=True)))

    @cached_property
    def bank_accounts(self):
        return list(self.org_bank_accounts.order_by('id').all())

    @cached_property
    def first_bank_account(self):
        return self.org_bank_accounts.order_by('id').first() or IssueOrgBankAccount()

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
    def issuer_affiliates_all(self):
        return [obj.__dict__ for obj in self.issuer_affiliates.all()]

    @cached_property
    def bg_property(self):
        bg_type = {
            'электронный аукцион': 'электронного аукциона',
            'открытый конкурс': 'открытого конкурса',
            'конкурс с ограниченным участием': 'конкурса с ограниченным участием',
            'аукцион в электронном виде': 'аукциона в электронном виде',
        }.get(self.tender_placement_type.lower(), self.tender_placement_type)
        issuer_head_fio = '%s %s %s' % (self.issuer_head_last_name, self.issuer_head_first_name, self.issuer_head_middle_name)
        if self.issuer_head_first_name and self.issuer_head_middle_name and  self.issuer_head_last_name:
            issuer_head_short_fio = '%s.%s. %s' % (self.issuer_head_first_name[0], self.issuer_head_middle_name[0], self.issuer_head_last_name)
        else:
            issuer_head_short_fio = ''

        sign_by = {
            'signer_1' : {
                'sign_by': 'Евграфова Ольга Алексеевна',
                'sign_by_rp': 'Евграфовой Ольги Алексеевны',
                'sign_by_short': 'О.А. Евграфова',
                'post_sign_by': 'Ведущий специалист Отдела документарных операций Управления развития документарных операций',
                'post_sign_by_rp': 'Ведущего специалиста Отдела документарных операций Управления развития документарных операций',
                'power_of_attorney': '№236 от 05 июня 2017 года',
            },
            'signer_2': {
                'sign_by': 'Голубев Дмитрий Алексеевич',
                'sign_by_rp': 'Голубева Дмитрия Алексеевича',
                'sign_by_short': 'Д. А. Голубев',
                'post_sign_by': 'Начальник Отдела документарных операций Управления развития документарных операций',
                'post_sign_by_rp': 'Начальника Отдела документарных операций Управления развития документарных операций',
                'power_of_attorney': '№235 от 05 июня 2017 года',
            },
            'signer_3': {
                'sign_by': 'Скворцова Ирина Вячеславовна',
                'sign_by_rp': 'Скворцовой Ирины Вячеславовны',
                'sign_by_short': 'И. В. Скворцова',
                'post_sign_by': 'Заместитель главного бухгалтера Московского филиала «БАНК СГБ»',
                'post_sign_by_rp': 'Заместителя главного бухгалтера Московского филиала «БАНК СГБ»',
                'power_of_attorney': '№30 от 25 января 2018 года',
            },
        }
        if self.bg_sum < 3000000:
            sign_by = sign_by['signer_1']
        elif 3000000 <= self.bg_sum < 13000000:
            sign_by = sign_by['signer_2']
        else:
            sign_by = sign_by['signer_3']
        properties = {
            'bg_number': generate_bg_number(self.created_at),
            'city': 'г. Москва',
            'bg_type': bg_type,
            'bg_sum_str': sum_str_format(self.bg_sum),
            'bank_commission_str': sum_str_format(self.bank_commission or 0),
            'indisputable': 'Гарант предоставляет Бенефициару право на бесспорное списание денежных средств со счета Гаранта, если Гарантом в течение пяти рабочих дней не исполнено требование Бенефициара об уплате денежной суммы по Гарантии, направленное с соблюдением условий Гарантии.' if self.is_indisputable_charge_off else 'Не указано в заявлениии',
            'requisites': '\n'.join([
                'Московский филиал «БАНК СГБ»',
                'Юридический (фактический) адрес: 121069, г. Москва,',
                'ул. Садовая-Кудринская, д. 2/62, стр.4',
                'ОГРН 1023500000160',
                'ИНН 3525023780, КПП 770343002',
                'К/с 30101810245250000094 в ГУ Банка России по ЦФО,',
                'БИК 044525094',
                'Телефон: (499) 951-49-40',
            ]),
            'issuer_head_short_fio': issuer_head_short_fio,
            'issuer_head_fio_rp': MorpherApi.get_response(issuer_head_fio, 'Р'),
            'issuer_head_post_rp': MorpherApi.get_response(self.issuer_head_org_position_and_permissions, 'Р').lower(),
            'arbitration': 'г. Москвы',
            'issuer_full_name_tp': MorpherApi.get_response(self.issuer_full_name, 'Т'),
            'tender_responsible_full_name_tp': MorpherApi.get_response(self.tender_responsible_full_name, 'Т'),
            'tender_placement_type_rp': MorpherApi.get_response(self.tender_placement_type, 'Р'),
            'tender_contract_subject_dp': MorpherApi.get_response(self.tender_contract_subject, 'Д'),
        }
        properties.update(sign_by)
        return properties

    @cached_property
    def underwriting_criteria(self):
        return CalculateUnderwritingCriteria().calc(self)

    @cached_property
    def bank_account_for_payment_fee(self):
        """
        Счет для оплаты банковской комиссии
        :return: string
        """
        return "70601810319002750311" if self.issuer_okopf.replace(' ', '') == '50102' else "70601810419002750211"

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

    def bg_contract_doc_admin_field(self):
        doc = self.bg_contract_doc
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
            if doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(doc.sign.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        output += ' <input type="file" name="bg_contract_doc_document" />'
        return output
    bg_contract_doc_admin_field.short_description = 'Договор'
    bg_contract_doc_admin_field.allow_tags = True

    def bg_doc_admin_field(self):
        doc = self.bg_doc
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
            if doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(doc.sign.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        output += ' <input type="file" name="bg_doc_document" />'
        return output
    bg_doc_admin_field.short_description = 'Проект'
    bg_doc_admin_field.allow_tags = True

    def approval_and_change_sheet_admin_field(self):
        doc = self.approval_and_change_sheet
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        return output
    approval_and_change_sheet_admin_field.short_description = 'Лист согласования и изменения БГ'
    approval_and_change_sheet_admin_field.allow_tags = True

    def payment_of_fee_admin_field(self):
        doc = self.payment_of_fee
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        output += ' <input type="file" name="bg_doc_document" />'
        return output
    payment_of_fee_admin_field.short_description = 'Счет'
    payment_of_fee_admin_field.allow_tags = True

    def contract_of_guarantee_admin_field(self):
        doc = self.contract_of_guarantee
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
            if doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(doc.sign.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        output += ' <input type="file" name="contract_of_guarantee_document" />'
        return output
    contract_of_guarantee_admin_field.short_description = 'Договор поручительства'
    contract_of_guarantee_admin_field.allow_tags = True

    def transfer_acceptance_act_admin_field(self):
        doc = self.transfer_acceptance_act
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
            if doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(doc.sign.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        output += ' <input type="file" name="transfer_acceptance_act_document" />'
        return output
    transfer_acceptance_act_admin_field.short_description = 'Акт'
    transfer_acceptance_act_admin_field.allow_tags = True

    def additional_doc_admin_field(self):
        doc = self.additional_doc
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
            if doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(doc.sign.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        output += ' <input type="file" name="additional_doc_document" />'
        return output
    additional_doc_admin_field.short_description = 'Дополнительно'
    additional_doc_admin_field.allow_tags = True

    def underwriting_criteria_doc_admin_field(self):
        doc = self.underwriting_criteria_doc
        field_parts = []
        if doc:
            if doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(doc.file.url))
            if doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(doc.sign.url))
        if len(field_parts) > 0:
            output = ', '.join(field_parts)
        else:
            output = 'отсутствует'
        output += ' <input type="file" name="underwriting_criteria_doc" />'
        return output
    underwriting_criteria_doc_admin_field.short_description = 'Критерии андеррайтинга'
    underwriting_criteria_doc_admin_field.allow_tags = True

    def doc_ops_mgmt_conclusion_doc_admin_field(self):
        field_parts = []
        if not self.doc_ops_mgmt_conclusion_doc:
            url = reverse('admin:marer_issue_generate_doc_ops_mgmt_conclusion_doc', args=(self.id,))
            field_parts.append('<b><a href="{}">сформировать</a></b>'.format(url))
        else:
            url = reverse('admin:marer_issue_generate_doc_ops_mgmt_conclusion_doc', args=(self.id,))
            field_parts.append('<b><a href="{}">переормировать</a></b>'.format(url))
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
            url = reverse('admin:marer_issue_generate_sec_dep_conclusion_doc', args=(self.id,))
            field_parts.append('<b><a href="{}">переормировать</a></b>'.format(url))
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

    def lawyers_dep_conclusion_doc_admin_field(self):
        field_parts = []
        if not self.lawyers_dep_conclusion_doc:
            url = reverse('admin:marer_issue_generate_lawyers_dep_conclusion_doc', args=(self.id,))
            field_parts.append('<b><a href="{}">сформировать</a></b>'.format(url))
        else:
            url = reverse('admin:marer_issue_generate_lawyers_dep_conclusion_doc', args=(self.id,))
            field_parts.append('<b><a href="{}">переормировать</a></b>'.format(url))
            if self.lawyers_dep_conclusion_doc.file:
                field_parts.append('<b><a href="{}">скачать</a></b>'.format(self.lawyers_dep_conclusion_doc.file.url))
            if self.lawyers_dep_conclusion_doc.sign:
                field_parts.append('<b><a href="{}">ЭЦП</a></b>'.format(self.lawyers_dep_conclusion_doc.sign.url))
        if len(field_parts) > 0:
            return ', '.join(field_parts)
        else:
            return 'отсутствует'
    lawyers_dep_conclusion_doc_admin_field.short_description = 'файл заключения ПУ'
    lawyers_dep_conclusion_doc_admin_field.allow_tags = True

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

    def check_all_application_required_fields_filled(self):
        checks = []
        checks.append(self.issuer_fact_address is not None and self.issuer_fact_address != '')
        checks.append(self.issuer_accountant_org_or_person is not None and self.issuer_accountant_org_or_person != '')
        checks.append(self.avg_employees_cnt_for_prev_year is not None and self.avg_employees_cnt_for_prev_year > 0)
        checks.append(self.issuer_head_passport_series is not None and self.issuer_head_passport_series != '')
        checks.append(self.issuer_head_passport_number is not None and self.issuer_head_passport_number != '')
        checks.append(self.issuer_head_passport_issue_date is not None)
        checks.append(self.issuer_head_residence_address is not None and self.issuer_head_residence_address != '')
        checks.append(self.issuer_head_passport_issued_by is not None and self.issuer_head_passport_issued_by != '')
        for tr in self.org_beneficiary_owners.all():
            checks.append(tr.legal_address is not None and tr.legal_address != '')
            checks.append(tr.fact_address is not None and tr.fact_address != '')
        return not False in checks

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
        if reg_form.is_valid() and self.check_stop_factors_validity:
            available_views.append('issue_survey')
        else:
            return available_views

        if self.application_doc_id is not None and self.check_all_application_required_fields_filled():
            available_views.append('issue_scoring')

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
        pdocs = []
        pdocs.extend(self.propose_documents.filter(type=consts.DOCUMENT_TYPE_FINANCE).order_by('name'))
        pdocs.extend(self.propose_documents.filter(type=consts.DOCUMENT_TYPE_LEGAL).order_by('name'))
        pdocs.extend(self.propose_documents.filter(type=consts.DOCUMENT_TYPE_OTHER).order_by('name'))
        return pdocs

    @property
    def propose_documents_app(self):
        return self.fill_app_docs()

    @property
    def propose_documents_fin(self):
        return self.propose_docs_by_type(consts.DOCUMENT_TYPE_FINANCE)

    @property
    def propose_documents_leg(self):
        return self.propose_docs_by_type(consts.DOCUMENT_TYPE_LEGAL)

    @property
    def propose_documents_oth(self):
        return self.propose_docs_by_type(consts.DOCUMENT_TYPE_OTHER)

    @property
    def is_leg_docs_listed_for_sign_by_client(self):
        return self.is_propose_document_list_approved_by_manager(self.propose_documents_leg)

    @property
    def is_fin_docs_listed_for_sign_by_client(self):
        return self.is_propose_document_list_approved_by_manager(self.propose_documents_fin)

    @property
    def is_oth_docs_listed_for_sign_by_client(self):
        return self.is_propose_document_list_approved_by_manager(self.propose_documents_oth)

    @property
    def is_application_docs_listed_for_sign_by_client(self):
        return self.is_propose_document_list_approved_by_manager(self.propose_documents_app)

    @property
    def propose_documents_for_remote_sign(self):
        docs = []
        docs.extend(self.fill_app_docs())
        if self.status == consts.ISSUE_STATUS_REVIEW:
            pdocs = self.propose_documents_ordered
            docs.extend(pdocs)
        return docs

    @property
    def is_application_filled(self):
        return bool(self.application_doc_id and self.application_doc.file)

    @property
    def is_application_signed(self):
        return self.application_doc_id and self.application_doc.sign and self.application_doc.sign_state == consts.DOCUMENT_SIGN_VERIFIED

    @property
    def is_all_propose_docs_filled(self):
        return not self.propose_documents.filter(Q(document__file__isnull=True) | Q(document__file='')).exists()

    @property
    def is_all_required_propose_docs_filled(self):
        return not self.propose_documents.filter(Q(document__file__isnull=True) | Q(document__file=''), is_required=True).exists()

    @property
    def can_send_for_review(self):
        return self.is_application_filled and self.is_application_signed and self.is_all_required_propose_docs_filled

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

    def fill_app_docs(self):
        docs = []
        if self.application_doc:
            docs.append(self.extend_propose_document(self.application_doc,
                                                     'Заявление на предоставление банковской гарантии',
                                                     4))
        if self.bg_doc and not self.status == consts.ISSUE_STATUS_REGISTERING:
            docs.append(self.extend_propose_document(self.bg_doc,
                                                     'Проект',
                                                     4))
        if self.transfer_acceptance_act and not self.status == consts.ISSUE_STATUS_REGISTERING:
            docs.append(self.extend_propose_document(self.transfer_acceptance_act,
                                                     'Акт',
                                                     4))
        if self.contract_of_guarantee and not self.status == consts.ISSUE_STATUS_REGISTERING:
            docs.append(self.extend_propose_document(self.contract_of_guarantee,
                                                     'Договор поручительства',
                                                     4))
        if self.approval_and_change_sheet and not self.status == consts.ISSUE_STATUS_REGISTERING:
            docs.append(self.extend_propose_document(self.approval_and_change_sheet,
                                                     'Лист согласования и изменения БГ',
                                                     4))
        return docs

    def extend_propose_document(self, doc, name, type):
        new_doc = IssueProposeDocument()
        new_doc.name = name
        new_doc.document = doc
        new_doc.type = type
        return new_doc

    @property
    def is_org_registered_more_than_6_months_ago(self):
        issuer_reg_delta = relativedelta(
            timezone.localdate(timezone.now(), timezone.get_current_timezone()),
            self.issuer_registration_date,
        )
        return not (issuer_reg_delta.years <= 0 and issuer_reg_delta.months < 6)

    @property
    def lawyers_executor_role(self):
        return 'Менеджер' if self.bg_sum < 5000000 else 'Юрист'

    @property
    def humanized_is_org_registered_more_than_6_months_ago(self):
        return 'Да' if self.is_org_registered_more_than_6_months_ago else 'Нет'

    @property
    def humanized_is_org_registered_less_than_6_months_ago(self):
        return 'Да' if not self.is_org_registered_more_than_6_months_ago else 'Нет'

    @property
    def humanuzed_is_org_activity_for_last_year_was_profilable(self):
        return 'Да' if self.balance_code_2400_offset_1 > 0 else 'Нет'

    @property
    def humanized_is_org_activity_for_last_year_was_not_profitable(self):
        return 'Да' if not self.balance_code_2400_offset_1 > 0 else 'Нет'

    @property
    def humanuzed_is_org_activity_for_last_period_was_profilable(self):
        return 'Да' if self.balance_code_2400_offset_0 > 0 else 'Нет'

    @property
    def is_issuer_in_blacklisted_region(self):
        for bl_inn_start in ['09', '01', '05', '06', '07', '15', '17', '20', '91', '92', '2632']:
            if self.issuer_inn.startswith(bl_inn_start):
                return True
        return False

    @property
    def is_beneficiary_in_blacklisted_region(self):
        for bl_inn_start in ['91', '92']:
            if self.tender_responsible_inn.startswith(bl_inn_start):
                return True
        return False

    @property
    def humanized_is_issuer_not_in_blacklisted_region(self):
        return 'Нет' if self.is_issuer_in_blacklisted_region else 'Да'

    @property
    def humanized_is_beneficiary_not_in_blacklisted_region(self):
        return 'Нет' if self.is_beneficiary_in_blacklisted_region else 'Да'

    @property
    def humanized_is_surety_needed(self):
        return 'требуется' if self.bg_sum >= 5000000 else 'не требуется'

    @property
    def bank_reserving_percent(self):
        percentage = {
            'Asgb': 1.25,
            'A2sgb': 1.25,
            'Bsgb': 2.25,
            'B2sgb': 2.75,
            'Esgb': 1.5,
            'E2sgb': 2.5,
            'Fsgb': 1.75,
            'F2sgb': 2.75,
            'Csgb': 2.75,
            'Dsgb': 7.25
        }

        return percentage.get(self.scoring_credit_rating, 7.25)

    @property
    def bank_reserving_percent_quality_category(self):
        categories = {
            'Asgb': '2',
            'A2sgb': '2',
            'Bsgb': '2',
            'B2sgb': '2',
            'Esgb': '2',
            'E2sgb': '2',
            'Fsgb': '2',
            'F2sgb': '2',
            'Csgb': '3',
            'Dsgb': '3'
        }

        return categories.get(self.scoring_credit_rating, 7.25)

    def is_propose_document_list_approved_by_manager(self, doc_list):
        is_exist = False
        for doc in doc_list:
            if doc.document and doc.is_approved_by_manager:
                is_exist = True
                break
        return is_exist

    def propose_docs_by_type(self, type):
        pdocs = []
        pdocs.extend(self.propose_documents.filter(type=type).order_by('name'))
        return pdocs

    def fill_doc_ops_mgmt_conclusion(self, commit=True, **kwargs):

        ve = ValidationError(None)
        ve.error_list = []
        if not self.is_org_registered_more_than_6_months_ago:
            ve.error_list.append('Обнаружен стоп-фактор: организация зарегистрирована менее 6 месецев назад')

        # if self.sec_dep_conclusion_doc is None or self.sec_dep_conclusion_doc.file is None:
        #     ve.error_list.append('Отсутствует заключение ДБ')

        if len(ve.error_list) > 0:
            raise ve

        if self.bg_sum < 1500000:
            domc_filename = 'issue_domc_up_to_1500000.docx'
        else:
            domc_filename = 'issue_domc_from_1500000.docx'

        template_path = os.path.join(
            settings.BASE_DIR,
            'marer',
            'templates',
            'documents',
            domc_filename
        )

        from marer.utils.documents import fill_docx_file_with_issue_data
        doc_ops_mgmt_conclusion_file = fill_docx_file_with_issue_data(template_path, self, **kwargs)
        doc_ops_mgmt_conclusion_file.name = 'doc_ops_mgmt_conclusion.docx'
        domc_doc = Document()
        domc_doc.file = doc_ops_mgmt_conclusion_file
        domc_doc.save()
        self.doc_ops_mgmt_conclusion_doc = domc_doc
        if commit:
            self.save()
        doc_ops_mgmt_conclusion_file.close()

    def fill_lawyers_dep_conclusion(self, commit=True, **kwargs):

        template_path = os.path.join(
            settings.BASE_DIR,
            'marer',
            'templates',
            'documents',
            'issue_lawyers_conclusion.docx'
        )

        from marer.utils.documents import fill_docx_file_with_issue_data
        lawyers_conclusion_file = fill_docx_file_with_issue_data(template_path, self, **kwargs)
        lawyers_conclusion_file.name = 'lawyers_conclusion.docx'
        lawyers_conclusion_doc = Document()
        lawyers_conclusion_doc.file = lawyers_conclusion_file
        lawyers_conclusion_doc.save()
        self.lawyers_dep_conclusion_doc = lawyers_conclusion_doc
        if commit:
            self.save()
        lawyers_conclusion_file.close()

    def fill_sec_dep_conclusion_doc(self, commit=True, **kwargs):

        ve = ValidationError(None)
        ve.error_list = []
        issuer_reg_delta = relativedelta(
            timezone.localdate(timezone.now(), timezone.get_current_timezone()),
            self.issuer_registration_date,
        )
        if not self.is_org_registered_more_than_6_months_ago:
            ve.error_list.append('Обнаружен стоп-фактор: организация зарегистрирована менее 6 месецев назад')

        if len(ve.error_list) > 0:
            raise ve

        if self.bg_sum < 500000:
            filename = 'issue_sec_dep_conclusion_up_to_500000.docx'
        elif self.bg_sum < 1500000:
            filename = 'issue_sec_dep_conclusion_more_500000_up_to_1500000.docx'
        elif self.bg_sum < 5000000:
            filename = 'issue_sec_dep_conclusion_more_1500000_up_to_5000000.docx'
        else:
            filename = 'issue_sec_dep_conclusion_more_5000000.docx'

        template_path = os.path.join(
            settings.BASE_DIR,
            'marer',
            'templates',
            'documents',
            filename
        )

        from marer.utils.documents import fill_docx_file_with_issue_data
        sec_dep_conclusion_file = fill_docx_file_with_issue_data(template_path, self, **kwargs)
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
            kontur_benefitiar_analytics_data = kontur_benefitiar_analytics_data.get('analytics', {})
            kontur_principal_analytics_data = kontur.analytics(inn=self.issuer_inn, ogrn=self.issuer_ogrn)
            kontur_principal_analytics_data = kontur_principal_analytics_data.get('analytics', {})

            # principal stop factors
            if kontur_principal_analytics_data.get('m4001', False):
                ve.error_list.append(
                    'Исполнитель найден в реестре недобросоветных поставщиков. '
                    'Рассмотрение заявки невозможно до устранения стоп-фактора.'
                )
            if kontur_principal_analytics_data.get('m7003', False):
                ve.error_list.append('Обнаружен стоп-фактор: организация зарегистрирована менее 6 месецев назад')
            if self.is_issuer_in_blacklisted_region:
                ve.error_list.append('Обнаружен стоп-фактор: исполнитель находится в необслуживаемом регионе')
            if kontur_principal_analytics_data.get('m5006', False):
                ve.error_list.append(
                    'Обнаружен стоп-фактор: указан недостоверный адрес исполнителя')

            # benefitiar stop factors
            if self.tender_exec_law in [consts.TENDER_EXEC_LAW_44_FZ, consts.TENDER_EXEC_LAW_223_FZ]:
                if kontur_benefitiar_analytics_data.get('q4005', 0) <= 0:
                    ve.error_list.append('Бенефициар не найден в реестре государственных заказчиков')
            for bl_inn_start in ['91', '92']:
                if self.tender_responsible_inn.startswith(bl_inn_start):
                    ve.error_list.append('Обнаружен стоп-фактор: заказчик находится в необслуживаемом регионе')
                    break

            if ((self.balance_code_2400_offset_1 or 0) < 0) or ((self.balance_code_2400_offset_0 or 0) < 0):
                ve.error_list.append('Обнаружен стоп-фактор: отрицательная прибыль')

        except Exception:
            ve.error_list.append('Не удалось проверить заявку на стоп-факторы')

        if len(ve.error_list) > 0:
            raise ve

    @cached_property
    def check_not_stop_factors(self):
        error_list = []

        try:
            kontur_principal_analytics_data = kontur.analytics(inn=self.issuer_inn, ogrn=self.issuer_ogrn).get('analytics', {})
            if kontur_principal_analytics_data.get('m5004', False):
                error_list.append([
                    'Организация была найдена в списке юридических лиц, имеющих задолженность по уплате налогов.', False
                ])
            if self.finished_contracts_count < settings.LIMIT_FINISHED_CONTRACTS:
                error_list.append(['Опыта нет. Необходимо загрузить документ подтверждающий опыт в пакете документов', True])
        except Exception:
            error_list.append(['Не удалось проверить заявку на стоп-факторы', False])

        return error_list

    @cached_property
    def check_stop_factors_validity(self):
        try:
            self.validate_stop_factors()
        except ValidationError:
            return False
        else:
            return True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, create_docs=True):
        if not self.bg_start_date:
            self.bg_start_date = timezone.now()
        if not self.product or self.product == '':
            self.product = BankGuaranteeProduct().name

        if self.check_all_application_required_fields_filled():
            self.fill_application_doc(commit=False)
            if self.old_application_doc is not None and self.application_doc is not None and self.old_application_doc.id != self.application_doc.id:
                identical = are_docx_files_identical(
                    self.old_application_doc.file.path,
                    self.application_doc.file.path
                )
                if identical:
                    self.application_doc = self.old_application_doc

        super().save(force_insert, force_update, using, update_fields)

        if create_docs and bool(self.propose_documents.exists() is False and self.tax_system):
            pdocs = FinanceOrgProductProposeDocument.objects.filter(
                Q(Q(tax_system=self.tax_system) | Q(tax_system__isnull=True)),
                Q(Q(min_bg_sum__lte=self.bg_sum) | Q(min_bg_sum__isnull=True)),
                Q(Q(max_bg_sum__gte=self.bg_sum) | Q(min_bg_sum__isnull=True)),
            )
            if self.finished_contracts_count >= settings.LIMIT_FINISHED_CONTRACTS:
                pdocs = pdocs.exclude(if_not_finished_contracts=True)
            if self.issuer_okopf:
                form_ownership = FormOwnership.objects.filter(okopf_codes__contains=self.issuer_okopf).first()
                pdocs = pdocs.filter(form_ownership__in=[form_ownership])
            for pdoc in pdocs:
                IssueProposeDocument.objects.get_or_create(issue=self, name=pdoc.name, defaults={
                    'code': pdoc.code,
                    'type': pdoc.type,
                    'is_required': pdoc.is_required,
                    'sample': pdoc.sample,
                })

    def __init__(self, *args, **kwargs):
        super(Issue, self).__init__(*args, **kwargs)
        self.old_status = self.status
        self.old_application_doc = self.application_doc


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
    type = models.PositiveIntegerField('тип документа', choices=consts.DOCUMENT_TYPE_CHOICES, default=consts.DOCUMENT_TYPE_OTHER, null=False, blank=False)
    is_required = models.BooleanField('обязательный документ', null=False, default=False)
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
        verbose_name = 'сообщение по заявке'
        verbose_name_plural = 'сообщения по заявке'

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='clarification_messages'
    )
    message = models.TextField(verbose_name='сообщение', blank=False, null=False, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='пользователь',
                             on_delete=models.DO_NOTHING, null=True)
    created_at = models.DateTimeField(verbose_name='время создания', auto_now_add=True, null=False)

    @property
    def user_repr(self):
        return self.user.__str__() if self.user else 'Клиент'

    @property
    def user_full_name_repr(self):
        return self.user.get_full_name() if self.user else 'Клиент'

    def __str__(self):
        return 'Сообщение по заявке №{num} от пользователя {user} в {created}'.format(
            num=self.issue_id,
            user=self.user,
            created=self.created_at,
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        set_obj_update_time(self.issue)
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
    inn = models.CharField(verbose_name='ИНН', max_length=512, blank=True, null=False, default='')
    bank_liabilities_vol = models.DecimalField(verbose_name='объем обязательств банка', max_digits=32, decimal_places=2, blank=True, null=True)


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


class IssueOrgManagementCollegial(models.Model):
    class Meta:
        verbose_name = 'коллегиальный исполнительный орган'
        verbose_name_plural = 'коллегиальные исполнительные органы'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False,
                              related_name='org_management_collegial')
    org_name = models.CharField(verbose_name='наименование', max_length=512,
                                blank=False, null=False, default='')
    fio = models.CharField(verbose_name='фио', max_length=512,
                           blank=False, null=False, default='')


class IssueOrgManagementDirectors(models.Model):
    class Meta:
        verbose_name = 'совет директоров'
        verbose_name_plural = 'совет директоров'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False,
                              related_name='org_management_directors')
    org_name = models.CharField(verbose_name='наименование', max_length=512,
                                blank=False, null=False, default='')
    fio = models.CharField(verbose_name='фио', max_length=512,
                           blank=False, null=False, default='')


class IssueOrgManagementOthers(models.Model):
    class Meta:
        verbose_name = 'иной орган управления'
        verbose_name_plural = 'иные органы управления'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False,
                              related_name='org_management_others')
    org_name = models.CharField(verbose_name='наименование', max_length=512,
                                blank=False, null=False, default='')
    fio = models.CharField(verbose_name='фио', max_length=512,
                           blank=False, null=False, default='')


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
    cost = models.DecimalField(verbose_name='сумма', max_digits=32, decimal_places=2, blank=True, null=True)


class IssueFactoringBuyer(models.Model):
    class Meta:
        verbose_name = 'покупатель на факторинговое обслуживание'
        verbose_name_plural = 'покупатели на факторинговое обслуживание'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='factoring_buyers')
    name_and_inn = models.CharField(verbose_name='наименование, ИНН', max_length=512, blank=False, null=False, default='')
    avg_monthly_shipments = models.CharField(verbose_name='средние отгрузки за последние 12 месяцев (млн руб. без НДС)', max_length=512, blank=True, null=False, default='')
    operating_pay_deferment_days = models.IntegerField(verbose_name='действующая отсрочка платежа, дней', blank=True, null=True)
    start_work_date = models.CharField(verbose_name='дата начала работы', max_length=512, blank=True, null=False, default='')
    required_credit_limit = models.DecimalField(verbose_name='требуемый кредитный лимит (млн руб. без НДС)', max_digits=32, decimal_places=2, blank=True, null=True)
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


class IssueMessagesProxy(Issue):
    class Meta:
        proxy = True
        verbose_name = 'собощение по заявке'
        verbose_name_plural = 'собощения по заявке'


@receiver(pre_save, sender=Issue, dispatch_uid="pre_save_issue")
def pre_save_issue(sender, instance, **kwargs):
    from marer.utils.documents import generate_doc
    if instance.old_status != instance.status and instance.status == consts.ISSUE_STATUS_REVIEW:
        from marer.utils.documents import generate_acts_for_issue
        instance.bg_property  # даем возможность выпасть исключению здесь, т.к. в format оно не появится
        generate_acts_for_issue(instance)


    if instance.status == consts.ISSUE_STATUS_REVIEW:
        from marer.utils.documents import generate_underwriting_criteria
        try:
            # исключениям выпадать не даем: пусть не заполняется целиком, если есть пропуски
            underwriting_criteria_doc, underwriting_criteria_score = generate_underwriting_criteria(instance)
            instance.underwriting_criteria_doc = underwriting_criteria_doc
            instance.underwriting_criteria_score = underwriting_criteria_score
        except Exception:
            pass

        if not instance.approval_and_change_sheet:
            instance.approval_and_change_sheet = generate_doc(
                os.path.join(settings.BASE_DIR, 'marer/templates/documents/acts/approval_and_change_sheet.docx'),
                'approval_and_change_sheet_%s.docx' % instance.id, instance)
