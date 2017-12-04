import importlib

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, RedirectView

from marer import forms
from marer.forms import RegisterSignForm
from marer.models.user import User
from marer.utils.crypto import extract_certificate_from_sign


class LoginView(TemplateView):
    template_name = 'marer/auth/login.html'

    def get(self, request, *args, **kwargs):
        login_form = forms.LoginForm()
        if 'login_form' not in kwargs:
            kwargs.update(dict(login_form=login_form))
        return super().get(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        login_form = forms.LoginForm(request.POST)

        login_form.full_clean()
        username = User.normalize_username(login_form.cleaned_data['email'])
        user_exists = User.objects.filter(username=username).exists()

        if not user_exists:
            login_form.add_error('email', 'Пользователь не найден')

        user = authenticate(
            request,
            username=username,
            password=login_form.cleaned_data['password']
        )
        if user is None and user_exists:
            login_form.add_error('password', 'Неверный пароль')

        if login_form.is_valid():
            login(request, user)
            url = reverse('cabinet_requests', args=args, kwargs=kwargs)
            url = request.GET.get('next', url)
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(login_form=login_form))
            return self.get(request=request, *args, **kwargs)


class LoginSignView(TemplateView):
    template_name = 'marer/auth/login_sign.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        login_form = forms.LoginSignForm()
        if 'login_form' not in kwargs:
            kwargs.update(dict(login_form=login_form))
        return super().get(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        login_form = forms.LoginSignForm(request.POST)

        if login_form.is_valid():
            user = None
            login_cert_hash = login_form.cleaned_data['cert']
            login_sign = login_form.cleaned_data['signature']
            login_cert = extract_certificate_from_sign(login_sign)
            try:
                user_for_check = User.objects.get(cert_hash=login_cert_hash)
                check_cert = extract_certificate_from_sign(user_for_check.cert_sign)
                if check_cert.digest('sha512') != login_cert.digest('sha512'):  # why it needed a bytes??
                    # user = user_for_check
                    login_form.add_error(None, 'Неверный сертификат')

                sign_is_correct = None
                raw_check_sign_class = settings.AUTH_CERT_SIGN_CHECK_CLASS
                if raw_check_sign_class is not None and raw_check_sign_class != '':
                    raw_check_sign_class = str(raw_check_sign_class)
                    check_sign_module_name, check_sign_class_name = raw_check_sign_class.rsplit('.', 1)
                    check_sign_module = importlib.import_module(check_sign_module_name)
                    check_sign_class = getattr(check_sign_module, check_sign_class_name)
                    sign_is_correct = check_sign_class.check_sign(login_sign)

                    if sign_is_correct:
                        user = user_for_check
                    elif sign_is_correct is False:
                        login_form.add_error(None, 'Неверная подпись')

                else:
                    login_form.add_error(None, 'Невозможно проверить подпись. Обратитесь в техническую поддержку.')


            except ObjectDoesNotExist:
                # signing registration
                if request.POST.get('reg_stage'):
                    register_form = RegisterSignForm(data=request.POST, initial=dict(
                        cert=login_cert_hash,
                        signature=login_sign
                    ))
                else:
                    register_form = RegisterSignForm(initial=dict(
                        cert=login_cert_hash,
                        signature=login_sign
                    ))
                if register_form.is_valid():
                    new_user = User()
                    new_user.first_name = register_form.cleaned_data['first_name']
                    new_user.last_name = register_form.cleaned_data['last_name']
                    new_user.email = register_form.cleaned_data['email']
                    new_user.username = User.normalize_username(register_form.cleaned_data['email'])
                    new_user.phone = register_form.cleaned_data['phone']
                    new_user.cert_hash = register_form.cleaned_data['cert']
                    new_user.cert_sign = register_form.cleaned_data['signature']
                    new_user.save()
                    user = new_user

                else:
                    kwargs['reg_form'] = register_form
                    self.template_name = 'marer/auth/register_sign.html'

            if user:
                login(request, user)
                url = reverse('cabinet_requests', args=args, kwargs=kwargs)
                return HttpResponseRedirect(url)

        kwargs.update(dict(login_form=login_form))
        return self.get(request=request, *args, **kwargs)


class RegisterView(TemplateView):
    template_name = 'marer/auth/register.html'

    def get(self, request, *args, **kwargs):
        reg_form = forms.RegisterForm()
        if 'reg_form' not in kwargs:
            kwargs.update(dict(reg_form=reg_form))
        return super().get(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        reg_form = forms.RegisterForm(request.POST)
        reg_form.full_clean()
        username = User.normalize_username(reg_form.cleaned_data['email'])
        user_exists = User.objects.filter(username=username).exists()
        if user_exists:
            reg_form.add_error('email', 'Пользователь с таким email уже существует ')
        if reg_form.is_valid():
            new_user = User()
            new_user.first_name = reg_form.cleaned_data['first_name']
            new_user.last_name = reg_form.cleaned_data['last_name']
            new_user.email = reg_form.cleaned_data['email']
            new_user.username = username
            new_user.phone = reg_form.cleaned_data['phone']
            new_user.set_password(reg_form.cleaned_data['password'])
            new_user.save()

            login(request, new_user)
            url = reverse('cabinet_requests', args=args, kwargs=kwargs)
            return HttpResponseRedirect(url)
        else:
            kwargs.update(dict(reg_form=reg_form))
            return self.get(request=request, *args, **kwargs)


class PasswordResetRequestView(TemplateView):
    template_name = 'marer/auth/password_reset_request.html'


class PasswordResetResetView(TemplateView):
    template_name = 'marer/auth/password_reset_reset.html'


class LogoutView(RedirectView):
    pattern_name = 'index'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)