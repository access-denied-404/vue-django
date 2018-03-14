from django.conf import settings
from django.db import models

from marer.models.base import Document


__all__ = ['Issuer', 'IssuerDocument']


class Issuer(models.Model):
    class Meta:
        verbose_name = 'принципал'
        verbose_name_plural = 'принципалы'

    inn = models.CharField('ИНН', max_length=32, blank=False, null=False)
    kpp = models.CharField('КПП', max_length=32, blank=False, null=False)
    ogrn = models.CharField('ОГРН', max_length=32, blank=False, null=False)
    full_name = models.CharField('полное наименование', max_length=512, blank=False, null=False)
    short_name = models.CharField('краткое наименование', max_length=512, blank=False, null=False)
    user = models.ForeignKey(verbose_name='закрепленный агент', to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{}, ИНН {}'.format(self.short_name, self.inn)


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
