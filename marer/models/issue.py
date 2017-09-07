from django.conf import settings
from django.db import models
from django.utils.formats import number_format

from marer.models.base import Document
from marer.models.issuer import Issuer, IssuerDocument
from marer.products import get_finance_products_as_choices, FinanceProduct, get_finance_products


__all__ = ['Issue', 'IssueDocument', 'IssueDocumentRequest']


class Issue(models.Model):
    STATUS_REGISTERING = 'registering'
    STATUS_COMMON_DOCUMENTS_REQUEST = 'common_documents_request'
    STATUS_SURVEY = 'survey'
    STATUS_SCORING = 'scoring'
    STATUS_ADDITIONAL_DOCUMENTS_REQUEST = 'additional_documents_request'
    STATUS_PAYMENTS = 'payments'
    STATUS_FINAL_DOCUMENTS_APPROVAL = 'final_documents_approval'
    STATUS_FINISHED = 'finished'
    STATUS_CANCELLED = 'cancelled'

    product = models.CharField(max_length=32, blank=False, null=False, choices=get_finance_products_as_choices())
    status = models.CharField(max_length=32, blank=False, null=False, choices=[
        (STATUS_REGISTERING, 'Оформление заявки'),
        (STATUS_COMMON_DOCUMENTS_REQUEST, 'Запрос документов'),
        (STATUS_SURVEY, 'Анкетирование'),
        (STATUS_SCORING, 'Скоринг'),
        (STATUS_ADDITIONAL_DOCUMENTS_REQUEST, 'Дозапрос документов'),
        (STATUS_PAYMENTS, 'Оплата услуг'),
        (STATUS_FINAL_DOCUMENTS_APPROVAL, 'Согласование итоговых документов'),
        (STATUS_FINISHED, 'Завершена'),
        (STATUS_CANCELLED, 'Отменена'),
    ])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False)
    sum = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    comment = models.TextField(blank=False, null=False, default='')

    issuer = models.ForeignKey(Issuer, on_delete=models.SET_NULL, blank=True, null=True)
    issuer_inn = models.CharField(max_length=32, blank=False, null=False)
    issuer_kpp = models.CharField(max_length=32, blank=False, null=False)
    issuer_ogrn = models.CharField(max_length=32, blank=False, null=False)
    issuer_full_name = models.CharField(max_length=512, blank=False, null=False)
    issuer_short_name = models.CharField(max_length=512, blank=False, null=False)

    @property
    def humanized_id(self):
        if self.id:
            return str(self.id).zfill(10)
        else:
            return 'БЕЗ НОМЕРА'

    @property
    def humanized_sum(self):
        if self.sum:
            fmt_sum = number_format(self.sum)
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
        return self.STATUS_REGISTERING

    def fill_from_issuer(self):
        self.issuer_inn = self.issuer.inn
        self.issuer_kpp = self.issuer.kpp
        self.issuer_ogrn = self.issuer.ogrn
        self.issuer_full_name = self.issuer.full_name
        self.issuer_short_name = self.issuer.short_name

    def get_product(self) -> FinanceProduct:
        for fp in get_finance_products():
            if fp.name == self.product:
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


class IssueFinanceOrgPropose:
    pass
