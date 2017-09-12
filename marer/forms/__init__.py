from django.forms import Form
from django.forms import fields
from django.forms.widgets import TextInput, PasswordInput, EmailInput, Select, Textarea

from marer.forms.widgets import CallableChoicesSelect
from marer.models.issue import Issue
from marer.models.user import User
from marer.products import get_finance_products_as_choices


class RegisterForm(Form):
    first_name = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Имя'
    )
    last_name = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Фамилия'
    )
    email = fields.EmailField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='E-mail'
    )
    phone = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Контактный телефон'
    )
    password = fields.CharField(
        required=True,
        widget=PasswordInput(attrs={'class': 'form-control'}),
        label='Пароль'
    )
    password_repeat = fields.CharField(
        required=True,
        widget=PasswordInput(attrs={'class': 'form-control'}),
        label='Пароль еще раз'
    )

    def is_valid(self):
        if self.data['password'] != self.data['password_repeat']:
            self.add_error(None, 'Введенные пароли не совпадают')
        return super().is_valid()


class LoginForm(Form):
    email = fields.EmailField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='E-mail'
    )
    password = fields.CharField(
        required=True,
        widget=PasswordInput(attrs={'class': 'form-control'}),
        label='Пароль'
    )


class ProfileForm(Form):
    first_name = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Имя'
    )
    last_name = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Фамилия'
    )
    phone = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Контактный телефон'
    )


class QuickRequestForm(Form):

    product = fields.CharField(
        required=True,
        widget=Select(
            choices=get_finance_products_as_choices(),
            attrs={'class': 'form-control'}
        ),
        label='Вид услуги'
    )
    issuer = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Название или ИНН органиазции'
    )
    contact_person_name = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Контактное лицо'
    )
    contact_phone = fields.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Телефон'
    )
    contact_email = fields.EmailField(
        required=True,
        widget=EmailInput(attrs={'class': 'form-control'}),
        label='E-mail'
    )

    def __init__(self, *args, user: User = None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.initial.update(dict(
                contact_person_name=user.get_full_name(),
                contact_email=user.email,
                contact_phone=user.phone,
            ))
            self.fields['contact_person_name'].disabled = True
            self.fields['contact_email'].disabled = True
            self.fields['contact_phone'].disabled = True


class CabinetIssueListFilterForm(Form):
    fpgrp = fields.CharField(
        required=False,
        widget=Select(
            choices=get_finance_products_as_choices(),
            attrs={'class': 'form-control', 'style': 'max-width: 300px;'}
        ),
        label='Вид заявки'
    )
    status = fields.CharField(
        required=False,
        widget=CallableChoicesSelect(
            choices=[
                (None, 'Все'),
                (Issue.STATUS_REGISTERING, 'Оформление заявки'),
                (Issue.STATUS_COMMON_DOCUMENTS_REQUEST, 'Запрос документов'),
                (Issue.STATUS_SURVEY, 'Анкетирование'),
                (Issue.STATUS_SCORING, 'Скоринг'),
                (Issue.STATUS_ADDITIONAL_DOCUMENTS_REQUEST, 'Дозапрос документов и разъяснений'),
                (Issue.STATUS_PAYMENTS, 'Оформление документов'),
                (Issue.STATUS_FINISHED, 'Завершена'),
                (Issue.STATUS_CANCELLED, 'Отменена'),
            ],
            attrs={'class': 'form-control'}
        ),
        label='Статус заявки'
    )


class IssueRegisteringForm(Form):
    product = fields.CharField(
        required=True,
        widget=Select(
            choices=get_finance_products_as_choices(),
            attrs={'class': 'form-control'}
        ),
        label='Вид заявки',
    )
    org_search_name = fields.CharField(
        required=False,
        widget=TextInput(attrs={'class': 'form-control'}),
        label='Организация',
    )
    comment = fields.CharField(
        required=False,
        widget=Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Комментарий к заявке',
    )


class RestTenderForm(Form):
    gos_number = fields.CharField(required=True, max_length=512)
