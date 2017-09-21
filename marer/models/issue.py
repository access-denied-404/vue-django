from django.conf import settings
from django.db import models
from django.utils.formats import number_format

from marer import consts
from marer.models.base import Document
from marer.models.finance_org import FinanceOrganization
from marer.models.issuer import Issuer, IssuerDocument
from marer.products import get_finance_products_as_choices, FinanceProduct, get_finance_products


__all__ = ['Issue', 'IssueDocument', 'IssueDocumentRequest']


class Issue(models.Model):
    product = models.CharField(max_length=32, blank=False, null=False, choices=get_finance_products_as_choices())
    status = models.CharField(max_length=32, blank=False, null=False, choices=[
        (consts.ISSUE_STATUS_REGISTERING, 'Оформление заявки'),
        (consts.ISSUE_STATUS_COMMON_DOCUMENTS_REQUEST, 'Запрос документов'),
        (consts.ISSUE_STATUS_SURVEY, 'Анкетирование'),
        (consts.ISSUE_STATUS_SCORING, 'Скоринг'),
        (consts.ISSUE_STATUS_ADDITIONAL_DOCUMENTS_REQUEST, 'Дозапрос документов'),
        (consts.ISSUE_STATUS_PAYMENTS, 'Оплата услуг'),
        (consts.ISSUE_STATUS_FINAL_DOCUMENTS_APPROVAL, 'Согласование итоговых документов'),
        (consts.ISSUE_STATUS_FINISHED, 'Завершена'),
        (consts.ISSUE_STATUS_CANCELLED, 'Отменена'),
    ])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False)
    comment = models.TextField(blank=False, null=False, default='')

    issuer = models.ForeignKey(Issuer, on_delete=models.SET_NULL, blank=True, null=True)
    issuer_inn = models.CharField(max_length=32, blank=False, null=False)
    issuer_kpp = models.CharField(max_length=32, blank=False, null=False)
    issuer_ogrn = models.CharField(max_length=32, blank=False, null=False)
    issuer_full_name = models.CharField(max_length=512, blank=False, null=False)
    issuer_short_name = models.CharField(max_length=512, blank=False, null=False)

    issuer_foreign_name = models.CharField(max_length=512, null=True)
    issuer_legal_address = models.CharField(max_length=512, null=True)
    issuer_fact_address = models.CharField(max_length=512, null=True)
    issuer_okpo = models.CharField(max_length=32, null=True)
    issuer_registration_date = models.CharField(max_length=32, null=True)
    issuer_ifns_reg_date = models.DateField(null=True)
    issuer_ifns_reg_cert_number = models.CharField(max_length=32, null=True)
    issuer_okopf = models.CharField(max_length=32, null=True)
    issuer_okved = models.CharField(max_length=32, null=True)

    issuer_head_first_name = models.CharField(max_length=512, null=True)
    issuer_head_last_name = models.CharField(max_length=512, null=True)
    issuer_head_middle_name = models.CharField(max_length=512, null=True)
    issuer_head_birthday = models.DateField(null=True)
    issuer_head_org_position_and_permissions = models.CharField(max_length=512, null=True)
    issuer_head_phone = models.CharField(max_length=512, null=True)
    issuer_head_passport_series = models.CharField(max_length=32, null=True)
    issuer_head_passport_number = models.CharField(max_length=32, null=True)
    issuer_head_passport_issue_date = models.DateField(null=True)
    issuer_head_passport_issued_by = models.CharField(max_length=512, null=True)
    issuer_head_residence_address = models.CharField(max_length=512, null=True)
    issuer_head_education_level = models.CharField(max_length=512, null=True)
    issuer_head_org_work_experience = models.CharField(max_length=512, null=True)
    issuer_head_share_in_authorized_capital = models.CharField(max_length=512, null=True)
    issuer_head_industry_work_experience = models.CharField(max_length=512, null=True)
    issuer_prev_org_info = models.CharField(max_length=512, null=True)

    tender_gos_number = models.CharField(max_length=32, null=True)
    tender_placement_type = models.CharField(max_length=512, null=True)
    tender_exec_law = models.CharField(max_length=32, null=True, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
    ])
    tender_publish_date = models.DateField(null=True)
    tender_start_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    tender_contract_type = models.CharField(max_length=32, null=True, choices=[
        (consts.TENDER_CONTRACT_TYPE_SUPPLY_CONTRACT, 'Поставка товара'),
        (consts.TENDER_CONTRACT_TYPE_SERVICE_CONTRACT, 'Оказание услуг'),
        (consts.TENDER_CONTRACT_TYPE_WORKS_CONTRACT, 'Выполнение работ'),
    ])
    tender_has_prepayment = models.NullBooleanField(null=True)

    tender_responsible_full_name = models.CharField(max_length=512, null=True)
    tender_responsible_legal_address = models.CharField(max_length=512, null=True)
    tender_responsible_inn = models.CharField(max_length=32, null=True)
    tender_responsible_kpp = models.CharField(max_length=32, null=True)
    tender_responsible_ogrn = models.CharField(max_length=32, null=True)

    bg_sum = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    bg_currency = models.CharField(max_length=32, null=True, choices=[
        (consts.CURRENCY_RUR, 'Рубль'),
        (consts.CURRENCY_USD, 'Доллар'),
        (consts.CURRENCY_EUR, 'Евро'),
    ])
    bg_start_date = models.DateField(null=True)
    bg_end_date = models.DateField(null=True)
    bg_deadline_date = models.DateField(null=True)
    bg_type = models.CharField(max_length=32, null=True, choices=[
        (consts.BG_TYPE_APPLICATION_ENSURE, 'Обеспечение заявки'),
        (consts.BG_TYPE_CONTRACT_EXECUTION, 'Исполнение контракта'),
    ])

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
            currency = 'руб.'
            return fmt_sum + ' ' + currency
        else:
            return '—'

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


class IssueDocument(models.Model):
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
        max_length=32,
        null=False,
        blank=False,
    )


class IssueDocumentRequest(models.Model):
    pass


class IssueFinanceOrgPropose(models.Model):
    class Meta:
        unique_together = (('issue', 'finance_org'),)

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False)
    finance_org = models.ForeignKey(FinanceOrganization, on_delete=models.CASCADE, blank=False, null=False)
