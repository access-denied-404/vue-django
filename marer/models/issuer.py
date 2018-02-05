from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from marer.models.base import Document


__all__ = ['Issuer', 'IssuerDocument', 'IssuerOrgCollegial', 'IssuerOrgDirector',
           'IssuerOrgOther', 'IssuerOrgBankAccount', 'IssuerFounderPhysical',
           'IssuerFounderLegal', 'IssuerBenOwner']


class Issuer(models.Model):
    inn = models.CharField(max_length=32, blank=False, null=False)
    kpp = models.CharField(max_length=32, blank=False, null=False)
    ogrn = models.CharField(max_length=32, blank=False, null=False)
    full_name = models.CharField(max_length=512, blank=False, null=False)
    short_name = models.CharField(max_length=512, blank=False, null=False)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    fact_address = models.CharField(verbose_name='Фактический адрес', max_length=512,
                                    blank=True, null=True, default='')
    accountant_org_or_person = models.CharField(verbose_name='ФИО бухгалтера или бух орг', max_length=512,
                                                       blank=True, null=True, default='')
    tax_system = models.CharField(verbose_name='Cистема налогообложения', max_length=512,
                                  blank=True, null=True, default='')
    has_overdue_debts_for_last_180_days = models.CharField(verbose_name='Наличие просроченной задолженности по всем'
                                                                        ' кредитам за последние 180 дней',
                                                           max_length=512, blank=True, null=True, default='')
    web_site = models.CharField(verbose_name='Web-сайт', max_length=512, blank=True, null=True, default='')
    avg_employees_cnt_for_prev_year = models.CharField(verbose_name='ср число работников за последний год', max_length=512,
                                                       blank=True, null=True, default='')
    post_address = models.CharField(verbose_name='почтовый адрес', max_length=512,
                                    blank=True, null=True, default='')
    okpo = models.CharField(verbose_name='ОКПО', max_length=32, blank=True, null=True, default='')
    okopf = models.CharField(verbose_name='ОКОПФ', max_length=32, blank=True, null=True, default='')
    legal_address = models.CharField(verbose_name='оф адрес', max_length=512,
                                     blank=True, null=True, default='')
    registration_date = models.CharField(verbose_name='дата регистрации', max_length=32,
                                         blank=True, null=True, default='')
    ifns_reg_date = models.CharField(verbose_name='дата регистрации в ИФНС', max_length=32,
                                     blank=True, null=True, default='')
    head_passport_series = models.CharField(verbose_name='серия паспорта руководителя', max_length=32,
                                            blank=True, null=True, default='')
    head_passport_number = models.CharField(verbose_name='номер паспорта руководителя', max_length=32,
                                            blank=True, null=True, default='')
    head_passport_issue_date = models.DateField(verbose_name='дата выдачи паспорта руководителя', blank=True, null=True)
    head_passport_issued_by = models.CharField(verbose_name='кем выдан паспорт руководителя', max_length=512,
                                               blank=True, null=True, default='')
    head_residence_address = models.CharField(verbose_name='адрес прописки руководителя', max_length=512,
                                              blank=True, null=True, default='')
    head_phone = models.CharField(verbose_name='cистема налогообложения', max_length=512,
                                  blank=True, null=True, default='')
    head_first_name = models.CharField(verbose_name='имя руководителя', max_length=512,
                                       blank=True, null=True, default='')
    head_last_name = models.CharField(verbose_name='фамилия руководителя', max_length=512,
                                      blank=True, null=True, default='')
    head_middle_name = models.CharField(verbose_name='отчество руководителя', max_length=512,
                                        blank=True, null=True, default='')
    head_org_position_and_permissions = models.CharField(verbose_name='должность, полномочия руководителя',
                                                         max_length=512, blank=True, null=True, default='')

    def get_name(self):
        if self.short_name != '':
            return self.short_name
        elif self.full_name != '':
            return self.full_name
        else:
            return 'Без названия'

    @property
    def org_collegials(self):
        return list(self.org_collegial.order_by('id').all())

    @property
    def org_directors(self):
        return list(self.org_director.order_by('id').all())

    @property
    def org_others(self):
        return list(self.org_other.order_by('id').all())

    @property
    def bank_accounts(self):
        return list(self.bank_account.order_by('id').all())

    @property
    def ben_owners(self):
        return list(self.ben_owner.order_by('id').all())

    @property
    def founders_legal(self):
        return list(self.founder_legal.order_by('id').all())

    @property
    def founders_physical(self):
        return list(self.founder_physical.order_by('id').all())

    @cached_property
    def collegial_org_name(self):
        return '\n'.join(list(self.org_collegial.all().values_list('org_name', flat=True)))

    @cached_property
    def collegial_fio(self):
        return '\n'.join(list(self.org_collegial.all().values_list('fio', flat=True)))

    @cached_property
    def directors_org_name(self):
        return '\n'.join(list(self.org_director.all().values_list('org_name', flat=True)))

    @cached_property
    def directors_fio(self):
        return '\n'.join(list(self.org_director.all().values_list('fio', flat=True)))

    @cached_property
    def others_org_name(self):
        return '\n'.join(list(self.org_other.all().values_list('org_name', flat=True)))

    @cached_property
    def others_fio(self):
        return '\n'.join(list(self.org_other.all().values_list('fio', flat=True)))


class IssuerOrgCollegial(models.Model):
    class Meta:
        verbose_name = 'коллегиальный исполнительный орган'
        verbose_name_plural = 'коллегиальные исполнительные органы'

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='org_collegial')
    org_name = models.CharField(verbose_name='наименование', max_length=512,
                                blank=False, null=True, default='')
    fio = models.CharField(verbose_name='фио', max_length=512,
                           blank=False, null=True, default='')


class IssuerOrgDirector(models.Model):
    class Meta:
        verbose_name = 'совет директоров'

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='org_director')
    org_name = models.CharField(verbose_name='наименование', max_length=512,
                                blank=False, null=True, default='')
    fio = models.CharField(verbose_name='фио', max_length=512,
                           blank=False, null=True, default='')


class IssuerOrgOther(models.Model):
    class Meta:
        verbose_name = 'иной орган управления'

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='org_other')
    org_name = models.CharField(verbose_name='наименование', max_length=512,
                                blank=False, null=True, default='')
    fio = models.CharField(verbose_name='фио', max_length=512,
                           blank=False, null=True, default='')


class IssuerOrgBankAccount(models.Model):
    class Meta:
        verbose_name = 'кредитная организация'

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='bank_account')
    bank_name = models.CharField(verbose_name='Банк', max_length=512, blank=True, null=True, default='')
    bank_identification_code = models.CharField(verbose_name='БИК', max_length=32,
                                                blank=True, null=True, default='')


class IssuerBenOwner(models.Model):
    class Meta:
        verbose_name = 'бенефициарный владелец'

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='ben_owner')
    fio = models.CharField(verbose_name='ФИО бен владельца', max_length=512, blank=False, null=True, default='')
    ben_legal_address = models.CharField(verbose_name='адрес регистрации бен владельца', max_length=512,
                                         blank=False, null=True, default='')
    ben_fact_address = models.CharField(verbose_name='адрес фактического пребывания бен владельца', max_length=512,
                                        blank=False, null=True, default='')
    ben_post_address = models.CharField(verbose_name='почтовый адрес бен владельца', max_length=512, blank=False,
                                        null=True, default='')
    ben_inn_or_snils = models.CharField(verbose_name='ИНН/СНИЛС (при наличии) бен владельца', max_length=512,
                                        blank=False, null=True, default='')


class IssuerFounderLegal(models.Model):
    class Meta:
        verbose_name = 'юридический учредитель компании'

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='founder_legal')
    founder_legal_name = models.CharField(verbose_name='наименование', max_length=512,
                                          blank=False, null=True, default='')
    founder_legal_auth_capital_percentage = models.CharField(verbose_name='доля в уставном капитале', max_length=512,
                                                             blank=False, null=True, default='')


class IssuerFounderPhysical(models.Model):
    class Meta:
        verbose_name = 'физический учредитель компании'

    issuer = models.ForeignKey(Issuer, on_delete=models.CASCADE, blank=False, null=False,
                               related_name='founder_physical')
    name = models.CharField(verbose_name='наименование', max_length=512,
                                         blank=False, null=True, default='')
    auth_capital_percentage = models.CharField(verbose_name='доля в уставном капитале',
                                                            max_length=512,
                                                            blank=False, null=True, default='')


class IssuerDocument(models.Model):
    issuer = models.ForeignKey(
        Issuer,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='issuer_documents'
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='issuer_links'
    )
    code = models.CharField(
        max_length=32,
        null=False,
        blank=False,
    )
