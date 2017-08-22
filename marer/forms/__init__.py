from django.forms import Form
from django.forms import fields
from django.forms.widgets import TextInput, PasswordInput, EmailInput

from marer.forms.widgets import CallableChoicesSelect
from marer.models import FinanceProduct


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


def get_finance_products_tree_for_select():
    fp_roots_list = FinanceProduct.objects.root_nodes()
    fp_tree = []
    for fp in fp_roots_list:
        if fp.childrens.exists():
            # fp_tree.append((fp.id, fp.name))
            fp_childs = fp.childrens.all()
            fp_tree.append((fp.name, [(fpc.id, fpc.name) for fpc in fp_childs]))
        else:
            fp_tree.append((fp.id, fp.name))
    return fp_tree


class QuickRequestForm(Form):

    finance_product = fields.CharField(
        required=True,
        widget=CallableChoicesSelect(
            choices=get_finance_products_tree_for_select,
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
