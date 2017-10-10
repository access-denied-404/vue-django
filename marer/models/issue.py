import json

from django.conf import settings
from django.db import models
from django.utils.formats import number_format

from marer import consts
from marer.models.base import Document
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
        (consts.ISSUE_STATUS_COMMON_DOCUMENTS_REQUEST, 'Запрос документов'),
        (consts.ISSUE_STATUS_SURVEY, 'Анкетирование'),
        (consts.ISSUE_STATUS_SCORING, 'Скоринг'),
        (consts.ISSUE_STATUS_ADDITIONAL_DOCUMENTS_REQUEST, 'Дозапрос документов'),
        (consts.ISSUE_STATUS_PAYMENTS, 'Оплата услуг'),
        (consts.ISSUE_STATUS_FINAL_DOCUMENTS_APPROVAL, 'Согласование итоговых документов'),
        (consts.ISSUE_STATUS_FINISHED, 'Завершена'),
        (consts.ISSUE_STATUS_CANCELLED, 'Отменена'),
    ])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='пользователь', on_delete=models.DO_NOTHING, null=False)
    comment = models.TextField(blank=True, null=False, default='')

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
    issuer_registration_date = models.CharField(verbose_name='дата регистрации', max_length=32, blank=True, null=False, default='')
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

    tender_gos_number = models.CharField(verbose_name='госномер тендера', max_length=32, blank=True, null=False, default='')
    tender_placement_type = models.CharField(verbose_name='способ определения поставщика в тендере', max_length=32, blank=True, null=False, default='')
    tender_exec_law = models.CharField(verbose_name='закон исполнения тендера', max_length=32, blank=True, null=True, choices=[
        (consts.TENDER_EXEC_LAW_44_FZ, '44-ФЗ'),
        (consts.TENDER_EXEC_LAW_223_FZ, '223-ФЗ'),
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

    def serialize_registering_data(self):
        reg_form_class = self.get_product().get_registering_form_class()
        reg_form = reg_form_class(self.__dict__)
        reg_form.full_clean()
        json_data = json.dumps(dict(
            formdata=reg_form.cleaned_data,
            errors=reg_form.errors,
        ), cls=CustomJSONEncoder)
        return json_data

    def __str__(self):
        if self.bg_sum:
            str_repr = 'Заявка №{num} на {sum} руб., {product} для {issuer}'
        else:
            str_repr = 'Заявка №{num}, {product} для {issuer}'
        return str_repr.format(
            num=self.id,
            sum=self.bg_sum,
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
        max_length=32,
        null=False,
        blank=False,
    )


class IssueFinanceOrgPropose(models.Model):
    class Meta:
        unique_together = (('issue', 'finance_org'),)
        verbose_name = 'предложение заявки в банк'
        verbose_name_plural = 'предложения заявок в банки'

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='proposes')
    finance_org = models.ForeignKey(FinanceOrganization, verbose_name='финансовая организация', on_delete=models.CASCADE, blank=False, null=False)

    formalize_note = models.TextField(verbose_name='подпись к документам для оформления', blank=True, null=False, default='')
    final_note = models.TextField(verbose_name='подпись к итоговым документам', blank=True, null=False, default='')
    final_decision = models.NullBooleanField(verbose_name='удовлетворена ли заявка', blank=True, null=True)


class IssueFinanceOrgProposeClarification(models.Model):
    class Meta:
        verbose_name = 'дозапрос'
        verbose_name_plural = 'дозапросы'

    propose = models.ForeignKey(
        IssueFinanceOrgPropose,
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
    created_at = models.DateTimeField(verbose_name='время создания', auto_now=True, null=False)

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


class IssueFinanceOrgProposeClarificationMessage(models.Model):
    clarification = models.ForeignKey(
        IssueFinanceOrgProposeClarification,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='clarification_messages'
    )
    message = models.TextField(blank=False, null=False, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField(auto_now=True, null=False)


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
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_affiliates')
    name = models.CharField(max_length=512, blank=False, null=False, default='')
    legal_address = models.CharField(max_length=512, blank=False, null=False, default='')
    inn = models.CharField(max_length=512, blank=False, null=False, default='')
    activity_type = models.CharField(max_length=512, blank=False, null=False, default='')
    aff_percentage = models.CharField(max_length=512, blank=False, null=False, default='')
    aff_type = models.CharField(max_length=512, blank=False, null=False, default='')


class IssueBGProdFounderLegal(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_founders_legal')
    name = models.CharField(max_length=512, blank=False, null=False, default='')
    add_date = models.CharField(max_length=512, blank=False, null=False, default='')
    additional_business = models.CharField(max_length=512, blank=False, null=False, default='')
    country = models.CharField(max_length=512, blank=False, null=False, default='')
    auth_capital_percentage = models.CharField(max_length=512, blank=False, null=False, default='')
    legal_address = models.CharField(max_length=512, blank=False, null=False, default='')


class IssueBGProdFounderPhysical(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, blank=False, null=False, related_name='issuer_founders_physical')
    fio = models.CharField(max_length=512, blank=False, null=False, default='')
    add_date = models.CharField(max_length=512, blank=False, null=False, default='')
    additional_business = models.CharField(max_length=512, blank=False, null=False, default='')
    country = models.CharField(max_length=512, blank=False, null=False, default='')
    auth_capital_percentage = models.CharField(max_length=512, blank=False, null=False, default='')
    address = models.CharField(max_length=512, blank=False, null=False, default='')
    passport_data = models.CharField(max_length=512, blank=False, null=False, default='')


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
