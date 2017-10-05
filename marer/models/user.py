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

    def __str__(self):
        user_name_list = []
        if self.first_name != '':
            user_name_list.append(self.first_name)
        if self.last_name != '':
            user_name_list.append(self.last_name)
        return ' '.join(user_name_list) + ', ' + self.get_username()
