from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Issuer(models.Model):
    inn = None
    kpp = None
    ogrn = None
    full_name = None
    short_name = None
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)


class Issue(models.Model):
    STATUS_REGISTERING = 'registering'
    STATUS_COMMON_DOCUMENTS_REQUEST = 'common_documents_request'
    STATUS_SURVEY = 'survey'
    STATUS_SCORING = 'scoring'
    STATUS_ADDITIONAL_DOCUMENTS_REQUEST = 'additional_documents_request'
    STATUS_PAYMENTS = 'payments'
    STATUS_FINAL_DOCUMENTS_APPROVAL = 'final_documents_approval'
    STATUS_FINISHED = 'finished'

    type = None
    status = None


# class User(AbstractUser):
#     phone = models.CharField(_('contact phone'), max_length=30, blank=True)



