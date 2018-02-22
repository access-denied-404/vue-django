import random
import string

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _


__all__ = ['User']


class User(AbstractUser):

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        permissions = [
            # права менеджеров, управляющих пользователями
            ('can_add_managed_users', 'Can add managed users'),
            ('can_change_users_base_info', 'Can change users base info'),
            ('can_change_managed_users', 'Can change managed users'),
            ('can_add_managed_users_issues', 'Can add managed users issues'),
            ('can_change_managed_users_issues', 'Can change managed users issues'),
            ('can_add_managed_users_issues_proposes', 'Can add managed users issues proposes'),
            ('can_view_managed_users_issues_proposes', 'Can view managed users issues proposes'),
            ('can_add_managed_users_issues_proposes_clarifications', 'Can add managed users issues proposes clarifications'),
            ('can_add_managed_users_issues_proposes_clarifications_messages', 'Can add managed users issues proposes clarifications messages'),
        ]

    phone = models.CharField('Контактный телефон', max_length=30, blank=True)
    legal_name = models.CharField('Наименование агента', max_length=512, blank=True, null=False, default='')
    middle_name = models.CharField('Отчество', max_length=30, blank=True, null=False, default='')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='менеджер пользователя',
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True
    )
    comment = models.TextField(verbose_name='комментарий', blank=True, null=False, default='')
    is_broker = models.BooleanField(
        'Статус брокера',
        default=False,
        help_text='Определяет, рассчитывается ли для пользователя комиссия и видит ли он свои выплаты, как брокер',
    )
    cert_hash = models.CharField(max_length=512, blank=True, null=False, default='')
    cert_sign = models.TextField(blank=True, null=False, default='')

    @classmethod
    def normalize_username(cls, username):
        username = super().normalize_username(username)
        return str(username).lower()

    def email_user(self, subject, message=None, from_email=None, html_template_filename=None, context=None, **kwargs):
        if html_template_filename is None:
            super().email_user(subject, message, from_email, **kwargs)
        else:
            msg_tmpl = get_template(html_template_filename)
            message = msg_tmpl.render(context or {})
            send_mail(subject, '', from_email, [self.email], html_message=message, **kwargs)

    def generate_new_password(self):
        new_pass = ''.join([random.choice(string.digits) for r in range(10)])
        self.set_password(new_pass)
        return new_pass

    def __str__(self):
        user_name_list = []
        if self.first_name != '':
            user_name_list.append(self.first_name)
        if self.last_name != '':
            user_name_list.append(self.last_name)
        return ' '.join(user_name_list) + ', ' + self.get_username()
