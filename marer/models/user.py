from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


__all__ = ['User']


class User(AbstractUser):
    phone = models.CharField(_('contact phone'), max_length=30, blank=True)

    @classmethod
    def normalize_username(cls, username):
        username = super().normalize_username(username)
        return str(username).lower()
