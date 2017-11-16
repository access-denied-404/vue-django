import json

from django.conf import settings
from django.db import models
from django.utils.formats import number_format

from marer import consts
from marer.models.base import Document, set_obj_update_time
from marer.models.finance_org import FinanceOrganization
from marer.models.issuer import Issuer, IssuerDocument
from marer.products import get_finance_products_as_choices, FinanceProduct, get_finance_products
from marer.utils import CustomJSONEncoder

__all__ = [
    'Issue', 'IssueDocument', 'IssueFinanceOrgPropose', 'IssueFinanceOrgProposeClarification',
    'IssueFinanceOrgProposeClarificationMessage', 'IssueFinanceOrgProposeClarificationMessageDocument'
]


class Issue(models.Model):
    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'заявки'

    product = models.CharField(verbose_name='банковский продукт', max_length=32, blank=False, null=False, choices=get_finance_products_as_choices())
    status = models.CharField(verbose_name='статус заявки', max_length=32, blank=False, null=False, choices=[
        (consts.ISSUE_STATUS_REGISTERING, 'Оформление заявки'),
        (consts.ISSUE_STATUS_REVIEW, 'Рассмотрение заявки'),
        (consts.ISSUE_STATUS_FINISHED, 'Завершена'),
        (consts.ISSUE_STATUS_CANCELLED, 'Отменена'),
    ], default=consts.ISSUE_STATUS_REGISTERING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='пользователь', on_delete=models.DO_NOTHING, null=False)
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
    # issuer_registration_date = models.CharField(verbose_name='дата регистрации', max_length=32, blank=True, null=False, default='')
    issuer_registration_date = models.DateField(verbose_name='дата рождения руководителя', blank=True, null=True)
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

    tender_gos_number = models.CharField(verbose_name='госномер или ссылка на тендер', max_length=32, blank=True, null=False, default='')
    tender_placement_type = models.CharField(verbose_name='способ определения поставщика в тендере', max_length=32, blank=True, null=False, default='')
    tender_exec_law = models.CharField(verbose_name='закон исполнения тендера', max_length=32, blank=True, null=True, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
        (consts.TENDER_EXEC_LAW_185_FZ, '185-ФЗ'),
        (consts.TENDER_EXEC_LAW_COMMERCIAL, 'Коммерческий'),
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
    factoring_avg_actual_buyers_payment_term = models.IntegerField(verbose_name='Срок лизинга (мес.)', blank=True, null=True)
    factoring_max_contract_deferred_payment_term = models.IntegerField(verbose_name='Срок лизинга (мес.)', blank=True, null=True)
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
        return self.get_status_display()

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
        json_data = json.dumps(dict(
            formdata=reg_form.cleaned_data,
            errors=reg_form.errors,
        ), cls=CustomJSONEncoder)
        return json_data

    @property
    def available_dashboard_views_names(self):
        registering_views = [
            'issue_registering',
            'issue_common_documents_request',
            'issue_survey',
            'issue_scoring',
        ]
        review_views = registering_views + [
            'issue_additional_documents_requests',
            'issue_payments',
            'issue_finished',
        ]
        if self.status == consts.ISSUE_STATUS_REGISTERING:
            return registering_views
        if self.status == consts.ISSUE_STATUS_REVIEW:
            return review_views
        if self.status in [consts.ISSUE_STATUS_FINISHED, consts.ISSUE_STATUS_CANCELLED]:
            return review_views
        else:
            return ['issue_registering']

    def editable_dashboard_views(self):
        registering_views = [
            'issue_registering',
            'issue_common_documents_request',
            'issue_survey',
            'issue_scoring',
        ]
        review_views = [
            'issue_scoring',
            'issue_additional_documents_requests',
            'issue_payments',
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


class IssueFinanceOrgPropose(models.Model):
    class Meta:
        unique_together = (('issue', 'finance_org'),)
        verbose_name = 'предложение заявки в банк'
        verbose_name_plural = 'предложения заявок в банки'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='proposes')
    finance_org = models.ForeignKey(FinanceOrganization, verbose_name='финансовая организация', on_delete=models.CASCADE, blank=False, null=False)
    updated_at = models.DateTimeField(verbose_name='время обновления', auto_now=True, null=False)
    created_at = models.DateTimeField(verbose_name='время создания', auto_now_add=True, null=False)

    formalize_note = models.TextField(verbose_name='подпись к документам для оформления', blank=True, null=False, default='')
    final_note = models.TextField(verbose_name='подпись к итоговым документам', blank=True, null=False, default='')
    final_decision = models.NullBooleanField(verbose_name='удовлетворена ли заявка', blank=True, null=True)

    def __str__(self):
        return 'Предложение заявки №{num} ({prod} на {sum} руб.) в {fin_org}'.format(
            num=self.issue.id,
            prod=self.issue.get_product().humanized_name,
            sum=self.issue.bg_sum,
            fin_org=self.finance_org.name
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.id and self.issue and self.issue.id and self.issue.status == consts.ISSUE_STATUS_REGISTERING and not self.issue.proposes.exists():
            self.issue.status = consts.ISSUE_STATUS_REVIEW
            self.issue.save()

        if not self.id:
            docs_samples = self.finance_org.products_docs_samples.filter(finance_product=self.issue.product)
        else:
            docs_samples = None

        set_obj_update_time(self.issue)
        super().save(force_insert, force_update, using, update_fields)

        if docs_samples:
            for ds in docs_samples:
                pdoc = IssueFinanceOrgProposeDocument()
                pdoc.propose = self
                pdoc.name = ds.name
                pdoc.sample = ds.sample
                pdoc.code = ds.code
                pdoc.save()

    @property
    def propose_documents_ordered(self):
        return self.propose_documents.order_by('document_id')  # need null to be first


class IssueFinanceOrgProposeDocument(models.Model):
    class Meta:
        verbose_name = 'документ для банка'
        verbose_name_plural = 'документы для банка'

    propose = models.ForeignKey(
        IssueFinanceOrgPropose,
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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, chain_docs_update=False):
        if not chain_docs_update and self.propose and self.propose.issue_id and self.document and self.document.file:
            other_proposes = self.propose.issue.proposes.all()
            if self.id:
                other_proposes = other_proposes.exclude(id=self.id)
            for propose in other_proposes:
                opdocs = propose.propose_documents.filter(code=self.code)
                for opdoc in opdocs:
                    opdoc.document = self.document
                    opdoc.save(chain_docs_update=True)

        super().save(force_insert, force_update, using, update_fields)


class IssueFinanceOrgProposeClarification(models.Model):
    class Meta:
        verbose_name = 'дозапрос'
        verbose_name_plural = 'дозапросы'

    propose = models.ForeignKey(
        IssueFinanceOrgPropose,
        verbose_name='предложение заявки в банк',
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
            self.propose.issue.id,
            self.propose.finance_org.name,
            self.created_at.strftime('%d.%m.%Y')
        )
        if self.initiator == consts.IFOPC_INITIATOR_ISSUER:
            return 'Дозапрос №{} по заявке №{} в {} от {}'.format(*str_args)
        else:
            return 'Дозапрос №{} по заявке №{} от {} от {}'.format(*str_args)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        set_obj_update_time(self.propose)
        return super().save(force_insert, force_update, using, update_fields)


class IssueFinanceOrgProposeClarificationMessage(models.Model):
    class Meta:
        verbose_name = 'сообщение по дозапросу'
        verbose_name_plural = 'сообщения по дозапросу'

    clarification = models.ForeignKey(
        IssueFinanceOrgProposeClarification,
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
        IssueFinanceOrgProposeClarificationMessage,
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
    legal_address = models.CharField(verbose_name='юридический адрес', max_length=512, blank=False, null=False, default='')
    inn = models.CharField(verbose_name='ИНН', max_length=512, blank=False, null=False, default='')
    activity_type = models.CharField(verbose_name='вид деятельности', max_length=512, blank=False, null=False, default='')
    aff_percentage = models.CharField(verbose_name='доля участия', max_length=512, blank=False, null=False, default='')
    aff_type = models.CharField(verbose_name='отношение к организации', max_length=512, blank=False, null=False, default='')


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
    add_date = models.CharField(verbose_name='дата внесения', max_length=512, blank=False, null=False, default='')
    additional_business = models.CharField(verbose_name='наличие других видов бизнеса', max_length=512, blank=False, null=False, default='')
    country = models.CharField(verbose_name='страна', max_length=512, blank=False, null=False, default='')
    auth_capital_percentage = models.CharField(verbose_name='доля в уставном капитале', max_length=512, blank=False, null=False, default='')
    legal_address = models.CharField(verbose_name='юридический адрес', max_length=512, blank=False, null=False, default='')


class IssueBGProdFounderPhysical(models.Model):
    class Meta:
        verbose_name = 'учредитель-физлицо'
        verbose_name_plural = 'учредители-физлица'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_founders_physical')
    fio = models.CharField(verbose_name='ФИО', max_length=512, blank=False, null=False, default='')
    add_date = models.CharField(verbose_name='дата внесения', max_length=512, blank=False, null=False, default='')
    additional_business = models.CharField(verbose_name='наличие других видов бизнеса', max_length=512, blank=False, null=False, default='')
    country = models.CharField(verbose_name='страна', max_length=512, blank=False, null=False, default='')
    auth_capital_percentage = models.CharField(verbose_name='доля в уставном капитале', max_length=512, blank=False, null=False, default='')
    address = models.CharField(verbose_name='адрес проживания', max_length=512, blank=False, null=False, default='')
    passport_data = models.CharField(verbose_name='паспортные данные', max_length=512, blank=False, null=False, default='')


class IssueFinanceOrgProposeFormalizeDocument(models.Model):
    class Meta:
        verbose_name = 'документ для оформления'
        verbose_name_plural = 'документы для оформления'

    propose = models.ForeignKey(
        IssueFinanceOrgPropose,
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
        related_name='propose_formalize_links'
    )


class IssueFinanceOrgProposeFinalDocument(models.Model):
    class Meta:
        verbose_name = 'итоговый документ'
        verbose_name_plural = 'итоговые документы'

    propose = models.ForeignKey(
        IssueFinanceOrgPropose,
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
        related_name='propose_final_links'
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
    avg_monthly_shipments = models.CharField(verbose_name='средние отгрузки за последние 12 месяцев (млн руб. без НДС)', max_length=512, blank=False, null=False, default='')
    operating_pay_deferment_days = models.IntegerField(verbose_name='действующая отсрочка платежа, дней', blank=True, null=True)
    start_work_date = models.CharField(verbose_name='дата начала работы', max_length=512, blank=False, null=False, default='')
    required_credit_limit = models.DecimalField(verbose_name='требуемый кредитный лимит (млн руб. без НДС)', max_digits=12, decimal_places=2, blank=True, null=True)
    debitor_share = models.CharField(verbose_name='доля дебитора', max_length=512, blank=False, null=False, default='')
    average_delay_days = models.IntegerField(verbose_name='средние просрочки за 12 месяцев, дней', blank=True, null=True)
    sales_volume = models.CharField(verbose_name='объем продаж за последние 12 месяцев (млн руб. без НДС)', max_length=512, blank=False, null=False, default='')
