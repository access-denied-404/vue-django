from django.conf import settings
from django.db import models

from marer.models.base import Document


__all__ = ['Issuer', 'IssuerDocument']


class Issuer(models.Model):
    inn = models.CharField(max_length=32, blank=False, null=False)
    kpp = models.CharField(max_length=32, blank=False, null=False)
    ogrn = models.CharField(max_length=32, blank=False, null=False)
    full_name = models.CharField(max_length=512, blank=False, null=False)
    short_name = models.CharField(max_length=512, blank=False, null=False)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)


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
